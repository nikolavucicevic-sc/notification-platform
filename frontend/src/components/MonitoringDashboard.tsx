import { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import api from '../services/api';
import './MonitoringDashboard.css';

interface HealthStatus {
  status: string;
  service: string;
  checks: {
    database?: { status: string; message: string };
    redis?: {
      status: string;
      message: string;
      queues?: { email_queue: number; sms_queue: number };
    };
  };
}

interface ServiceHealth {
  name: string;
  status: 'healthy' | 'unhealthy' | 'loading';
  endpoint: string;
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
  email_dlq: { count: number; messages: DLQMessage[] };
  sms_dlq: { count: number; messages: DLQMessage[] };
  total_failed: number;
}

interface NotificationStats {
  total: number;
  by_status: Record<string, number>;
  by_channel: Record<string, number>;
  recent: {
    id: string;
    type: string;
    status: string;
    subject?: string;
    recipient_count: number;
    created_at: string;
  }[];
}

const STATUS_COLORS: Record<string, string> = {
  completed: 'var(--success)',
  failed: 'var(--danger)',
  processing: 'var(--warning, #f59e0b)',
  pending: 'var(--text-muted)',
};

const MAX_SPARKLINE = 20;

export function MonitoringDashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [services, setServices] = useState<ServiceHealth[]>([
    { name: 'Customer Service', status: 'loading', endpoint: '/api/health/customers' },
    { name: 'Scheduler Service', status: 'loading', endpoint: '/api/health/scheduler' },
    { name: 'Template Service', status: 'loading', endpoint: '/api/health/templates' },
  ]);
  const [dlq, setDlq] = useState<DLQResponse | null>(null);
  const [stats, setStats] = useState<NotificationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const queueHistory = useRef<{ email: number[]; sms: number[] }>({ email: [], sms: [] });

  useEffect(() => {
    fetchData();
    if (autoRefresh) {
      const interval = setInterval(fetchData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const fetchData = async () => {
    try {
      const [healthRes, dlqRes, statsRes] = await Promise.all([
        api.get('/health/'),
        api.get('/dlq/'),
        api.get('/notifications/stats/summary'),
      ]);

      setHealth(healthRes.data);
      setDlq(dlqRes.data);
      setStats(statsRes.data);

      // Track queue depth history for sparkline
      const queues = healthRes.data?.checks?.redis?.queues;
      if (queues) {
        const h = queueHistory.current;
        h.email = [...h.email, queues.email_queue].slice(-MAX_SPARKLINE);
        h.sms = [...h.sms, queues.sms_queue].slice(-MAX_SPARKLINE);
      }

      setLastUpdated(new Date());
      setLoading(false);
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
      setLoading(false);
    }

    // Fetch other service health independently so one failure doesn't block the rest
    const serviceEndpoints = [
      { name: 'Customer Service', endpoint: '/api/health/customers' },
      { name: 'Scheduler Service', endpoint: '/api/health/scheduler' },
      { name: 'Template Service', endpoint: '/api/health/templates' },
    ];
    const results = await Promise.allSettled(
      serviceEndpoints.map(s => api.get(s.endpoint.replace('/api', '')))
    );
    setServices(serviceEndpoints.map((s, i) => ({
      ...s,
      status: results[i].status === 'fulfilled' ? 'healthy' : 'unhealthy',
    })));
  };

  const retryMessage = async (channel: string, notificationId: string) => {
    try {
      const response = await api.post(`/dlq/retry/${channel}/${notificationId}`);
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
      const response = await api.delete(`/dlq/clear/${channel}`);
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

  const formatTimestamp = (ts?: number | string) => {
    if (!ts) return 'N/A';
    const d = typeof ts === 'number' ? new Date(ts * 1000) : new Date(ts);
    return d.toLocaleString();
  };

  const renderSparkline = (values: number[], color: string) => {
    if (values.length < 2) return null;
    const max = Math.max(...values, 1);
    const w = 80, h = 28;
    const pts = values.map((v, i) => {
      const x = (i / (values.length - 1)) * w;
      const y = h - (v / max) * h;
      return `${x},${y}`;
    }).join(' ');
    return (
      <svg width={w} height={h} style={{ display: 'block' }}>
        <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" />
      </svg>
    );
  };

  if (loading) return <div className="monitoring-dashboard"><p>Loading monitoring data...</p></div>;

  const allHealthy =
    health?.status === 'healthy' && services.every(s => s.status === 'healthy');

  return (
    <div className="monitoring-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h2>System Monitoring</h2>
          {lastUpdated && (
            <span className="last-updated">Updated {lastUpdated.toLocaleTimeString()}</span>
          )}
        </div>
        <label className="auto-refresh-toggle">
          <input type="checkbox" checked={autoRefresh} onChange={e => setAutoRefresh(e.target.checked)} />
          <span>Auto-refresh (5s)</span>
        </label>
      </div>

      {/* Overall status banner */}
      <div className={`status-banner ${allHealthy ? 'banner-healthy' : 'banner-unhealthy'}`}>
        <div className={`status-indicator ${allHealthy ? 'healthy' : 'unhealthy'}`} />
        <span>{allHealthy ? 'All systems operational' : 'Some services need attention'}</span>
      </div>

      {/* Notification Stats */}
      {stats && (
        <div className="monitoring-section">
          <h3>Notification Overview</h3>
          <div className="stats-grid">
            <div className="stat-box">
              <span className="stat-label">Total</span>
              <span className="stat-value">{stats.total.toLocaleString()}</span>
            </div>
            {Object.entries(stats.by_status).map(([status, count]) => (
              <div className="stat-box" key={status}>
                <span className="stat-label">{status.charAt(0).toUpperCase() + status.slice(1)}</span>
                <span className="stat-value" style={{ color: STATUS_COLORS[status] || 'inherit' }}>
                  {count.toLocaleString()}
                </span>
              </div>
            ))}
            {Object.entries(stats.by_channel).map(([channel, count]) => (
              <div className="stat-box" key={channel}>
                <span className="stat-label">{channel.toUpperCase()}</span>
                <span className="stat-value">{count.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Service Health */}
      <div className="monitoring-section">
        <h3>Service Health</h3>
        <div className="services-grid">
          {/* Notification service (main) */}
          <div className={`service-card ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
            <div className="service-card-header">
              <div className={`status-indicator ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`} />
              <span className="service-name">Notification Service</span>
            </div>
            {health?.checks.database && (
              <div className="service-detail">
                <span className={`detail-dot ${health.checks.database.status}`} />
                DB: {health.checks.database.message}
              </div>
            )}
            {health?.checks.redis && (
              <div className="service-detail">
                <span className={`detail-dot ${health.checks.redis.status}`} />
                Redis: {health.checks.redis.message}
              </div>
            )}
            {health?.checks.redis?.queues && (
              <div className="queue-row">
                <div className="queue-item">
                  <div className="queue-label">Email Queue</div>
                  <div className="queue-count">{health.checks.redis.queues.email_queue}</div>
                  {renderSparkline(queueHistory.current.email, 'var(--primary)')}
                </div>
                <div className="queue-item">
                  <div className="queue-label">SMS Queue</div>
                  <div className="queue-count">{health.checks.redis.queues.sms_queue}</div>
                  {renderSparkline(queueHistory.current.sms, 'var(--success)')}
                </div>
              </div>
            )}
          </div>

          {/* Other services */}
          {services.map(service => (
            <div key={service.name} className={`service-card ${service.status}`}>
              <div className="service-card-header">
                <div className={`status-indicator ${service.status === 'loading' ? 'loading' : service.status}`} />
                <span className="service-name">{service.name}</span>
              </div>
              <div className="service-status-text">
                {service.status === 'loading' ? 'Checking...' : service.status.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      {stats && stats.recent.length > 0 && (
        <div className="monitoring-section">
          <h3>Recent Activity</h3>
          <div className="activity-feed">
            {stats.recent.map(n => (
              <div key={n.id} className="activity-item">
                <div className="activity-left">
                  <span className={`activity-badge badge-${n.type.toLowerCase()}`}>{n.type}</span>
                  <div className="activity-info">
                    <span className="activity-subject">{n.subject || n.type + ' notification'}</span>
                    <span className="activity-meta">{n.recipient_count} recipient{n.recipient_count !== 1 ? 's' : ''} · {formatTimestamp(n.created_at)}</span>
                  </div>
                </div>
                <span className={`activity-status status-${n.status.toLowerCase()}`}>{n.status}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Dead Letter Queue */}
      <div className="monitoring-section">
        <h3>Dead Letter Queue</h3>
        {dlq && dlq.total_failed === 0 ? (
          <div className="empty-state">No failed notifications in the queue</div>
        ) : (
          <>
            <div className="dlq-summary">
              <div className="dlq-stat">
                <span className="stat-label">Total Failed</span>
                <span className="stat-value" style={{ color: 'var(--danger)' }}>{dlq?.total_failed}</span>
              </div>
              <div className="dlq-stat">
                <span className="stat-label">Email DLQ</span>
                <span className="stat-value">{dlq?.email_dlq.count}</span>
              </div>
              <div className="dlq-stat">
                <span className="stat-label">SMS DLQ</span>
                <span className="stat-value">{dlq?.sms_dlq.count}</span>
              </div>
            </div>

            {dlq && dlq.email_dlq.count > 0 && (
              <div className="dlq-channel">
                <div className="dlq-channel-header">
                  <h4>Email DLQ ({dlq.email_dlq.count})</h4>
                  <button onClick={() => clearDLQ('email')} className="btn-danger-small">Clear All</button>
                </div>
                <div className="dlq-messages">
                  {dlq.email_dlq.messages.map(msg => (
                    <div key={msg.dlq_index} className="dlq-message">
                      <div className="dlq-message-header">
                        <span className="notification-id">{msg.notification_id}</span>
                        <button onClick={() => retryMessage('email', msg.notification_id)} className="btn-retry">Retry</button>
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

            {dlq && dlq.sms_dlq.count > 0 && (
              <div className="dlq-channel">
                <div className="dlq-channel-header">
                  <h4>SMS DLQ ({dlq.sms_dlq.count})</h4>
                  <button onClick={() => clearDLQ('sms')} className="btn-danger-small">Clear All</button>
                </div>
                <div className="dlq-messages">
                  {dlq.sms_dlq.messages.map(msg => (
                    <div key={msg.dlq_index} className="dlq-message">
                      <div className="dlq-message-header">
                        <span className="notification-id">{msg.notification_id}</span>
                        <button onClick={() => retryMessage('sms', msg.notification_id)} className="btn-retry">Retry</button>
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
