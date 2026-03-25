import { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import './MonitoringDashboard.css';

interface HealthStatus {
  status: string;
  service: string;
  checks: {
    database?: { status: string; message: string };
    redis?: {
      status: string;
      message: string;
      queues?: {
        email_queue: number;
        sms_queue: number;
      };
    };
  };
}

interface DLQMessage {
  notification_id: string;
  channel: string;
  subject?: string;
  body: string;
  customer_ids: string[];
  failure_reason?: string;
  failed_at?: number;
  total_attempts?: number;
  dlq_index: number;
}

interface DLQResponse {
  email_dlq: {
    count: number;
    messages: DLQMessage[];
  };
  sms_dlq: {
    count: number;
    messages: DLQMessage[];
  };
  total_failed: number;
}

export function MonitoringDashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [dlq, setDlq] = useState<DLQResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    fetchData();

    if (autoRefresh) {
      const interval = setInterval(fetchData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchData = async () => {
    try {
      const [healthRes, dlqRes] = await Promise.all([
        axios.get('/api/health/'),
        axios.get('/api/dlq/')
      ]);

      setHealth(healthRes.data);
      setDlq(dlqRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
      setLoading(false);
    }
  };

  const retryMessage = async (channel: string, notificationId: string) => {
    try {
      const response = await axios.post(`/api/dlq/retry/${channel}/${notificationId}`);

      if (response.data.success) {
        toast.success(`Notification ${notificationId} queued for retry`);
        fetchData();
      } else {
        toast.error(response.data.message);
      }
    } catch (error: any) {
      toast.error(`Failed to retry: ${error.response?.data?.message || error.message}`);
    }
  };

  const clearDLQ = async (channel: string) => {
    if (!confirm(`Are you sure you want to clear all ${channel} DLQ messages?`)) return;

    try {
      const response = await axios.delete(`/api/dlq/clear/${channel}`);

      if (response.data.success) {
        toast.success(response.data.message);
        fetchData();
      } else {
        toast.error(response.data.message);
      }
    } catch (error: any) {
      toast.error(`Failed to clear DLQ: ${error.response?.data?.message || error.message}`);
    }
  };

  const formatTimestamp = (timestamp?: number) => {
    if (!timestamp) return 'N/A';
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (loading) {
    return <div className="monitoring-dashboard"><p>Loading monitoring data...</p></div>;
  }

  return (
    <div className="monitoring-dashboard">
      <div className="dashboard-header">
        <h2>🔧 System Monitoring</h2>
        <label className="auto-refresh-toggle">
          <input
            type="checkbox"
            checked={autoRefresh}
            onChange={(e) => setAutoRefresh(e.target.checked)}
          />
          <span>Auto-refresh (5s)</span>
        </label>
      </div>

      {/* Health Status */}
      <div className="monitoring-section">
        <h3>Service Health</h3>
        <div className={`health-card ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
          <div className="health-status">
            <span className="status-icon">{health?.status === 'healthy' ? '✅' : '❌'}</span>
            <span className="status-text">{health?.status?.toUpperCase()}</span>
          </div>

          <div className="health-checks">
            {health?.checks.database && (
              <div className={`check ${health.checks.database.status}`}>
                <strong>Database:</strong> {health.checks.database.message}
              </div>
            )}

            {health?.checks.redis && (
              <div className={`check ${health.checks.redis.status}`}>
                <strong>Redis:</strong> {health.checks.redis.message}
                {health.checks.redis.queues && (
                  <div className="queue-depths">
                    <span>Email Queue: {health.checks.redis.queues.email_queue}</span>
                    <span>SMS Queue: {health.checks.redis.queues.sms_queue}</span>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dead Letter Queue */}
      <div className="monitoring-section">
        <h3>Dead Letter Queue (Failed Notifications)</h3>

        {dlq && dlq.total_failed === 0 ? (
          <div className="empty-state">✅ No failed notifications</div>
        ) : (
          <>
            <div className="dlq-summary">
              <div className="dlq-stat">
                <span className="stat-label">Total Failed:</span>
                <span className="stat-value">{dlq?.total_failed}</span>
              </div>
              <div className="dlq-stat">
                <span className="stat-label">Email DLQ:</span>
                <span className="stat-value">{dlq?.email_dlq.count}</span>
              </div>
              <div className="dlq-stat">
                <span className="stat-label">SMS DLQ:</span>
                <span className="stat-value">{dlq?.sms_dlq.count}</span>
              </div>
            </div>

            {/* Email DLQ Messages */}
            {dlq && dlq.email_dlq.count > 0 && (
              <div className="dlq-channel">
                <div className="dlq-channel-header">
                  <h4>📧 Email DLQ ({dlq.email_dlq.count})</h4>
                  <button
                    onClick={() => clearDLQ('email')}
                    className="btn-danger-small"
                  >
                    Clear All
                  </button>
                </div>

                <div className="dlq-messages">
                  {dlq.email_dlq.messages.map((msg) => (
                    <div key={msg.dlq_index} className="dlq-message">
                      <div className="dlq-message-header">
                        <span className="notification-id">{msg.notification_id}</span>
                        <button
                          onClick={() => retryMessage('email', msg.notification_id)}
                          className="btn-retry"
                        >
                          🔄 Retry
                        </button>
                      </div>

                      {msg.subject && <p><strong>Subject:</strong> {msg.subject}</p>}
                      <p><strong>Body:</strong> {msg.body.substring(0, 100)}...</p>
                      <p><strong>Recipients:</strong> {msg.customer_ids.length} customer(s)</p>
                      {msg.failure_reason && <p className="failure-reason"><strong>Error:</strong> {msg.failure_reason}</p>}
                      {msg.total_attempts && <p><strong>Attempts:</strong> {msg.total_attempts}</p>}
                      {msg.failed_at && <p><strong>Failed At:</strong> {formatTimestamp(msg.failed_at)}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* SMS DLQ Messages */}
            {dlq && dlq.sms_dlq.count > 0 && (
              <div className="dlq-channel">
                <div className="dlq-channel-header">
                  <h4>📱 SMS DLQ ({dlq.sms_dlq.count})</h4>
                  <button
                    onClick={() => clearDLQ('sms')}
                    className="btn-danger-small"
                  >
                    Clear All
                  </button>
                </div>

                <div className="dlq-messages">
                  {dlq.sms_dlq.messages.map((msg) => (
                    <div key={msg.dlq_index} className="dlq-message">
                      <div className="dlq-message-header">
                        <span className="notification-id">{msg.notification_id}</span>
                        <button
                          onClick={() => retryMessage('sms', msg.notification_id)}
                          className="btn-retry"
                        >
                          🔄 Retry
                        </button>
                      </div>

                      <p><strong>Message:</strong> {msg.body.substring(0, 100)}...</p>
                      <p><strong>Recipients:</strong> {msg.customer_ids.length} customer(s)</p>
                      {msg.failure_reason && <p className="failure-reason"><strong>Error:</strong> {msg.failure_reason}</p>}
                      {msg.total_attempts && <p><strong>Attempts:</strong> {msg.total_attempts}</p>}
                      {msg.failed_at && <p><strong>Failed At:</strong> {formatTimestamp(msg.failed_at)}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
