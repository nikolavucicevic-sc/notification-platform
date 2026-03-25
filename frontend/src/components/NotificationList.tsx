import React, { useEffect, useState, useRef } from 'react';
import { Notification, NotificationStatus } from '../types/notification';
import { notificationApi } from '../services/api';
import { usePolling } from '../hooks/usePolling';
import toast from 'react-hot-toast';

interface NotificationListProps {
  refreshTrigger: number;
}

const NotificationList: React.FC<NotificationListProps> = ({ refreshTrigger }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pollingEnabled, setPollingEnabled] = useState(true);
  const previousStatuses = useRef<Map<string, NotificationStatus>>(new Map());

  const fetchNotifications = async () => {
    if (!loading) {
      setLoading(true);
    }
    setError(null);
    try {
      const data = await notificationApi.getNotifications();
      const sorted = data.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );

      // Check for status changes and show toast notifications
      sorted.forEach(notification => {
        const prevStatus = previousStatuses.current.get(notification.id);
        if (prevStatus && prevStatus !== notification.status) {
          // Status changed!
          if (notification.status === NotificationStatus.COMPLETED) {
            toast.success(`Notification "${notification.subject}" completed!`);
          } else if (notification.status === NotificationStatus.FAILED) {
            toast.error(`Notification "${notification.subject}" failed`);
          } else if (notification.status === NotificationStatus.PROCESSING) {
            toast.loading(`Processing "${notification.subject}"...`, { duration: 2000 });
          }
        }
        previousStatuses.current.set(notification.id, notification.status);
      });

      setNotifications(sorted);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch notifications');
      toast.error('Failed to refresh notifications');
    } finally {
      setLoading(false);
    }
  };

  // Poll every 5 seconds
  usePolling(fetchNotifications, 5000, pollingEnabled);

  // Also fetch when refreshTrigger changes (manual refresh)
  useEffect(() => {
    fetchNotifications();
  }, [refreshTrigger]);

  const getStatusBadgeClass = (status: NotificationStatus) => {
    switch (status) {
      case NotificationStatus.COMPLETED:
        return 'status-badge status-completed';
      case NotificationStatus.PROCESSING:
        return 'status-badge status-processing';
      case NotificationStatus.PENDING:
        return 'status-badge status-pending';
      case NotificationStatus.FAILED:
        return 'status-badge status-failed';
      default:
        return 'status-badge';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (error && notifications.length === 0) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="notification-list">
      <div className="list-header">
        <div>
          <h2>📨 Notifications</h2>
          <div className="polling-indicator">
            <label>
              <input
                type="checkbox"
                checked={pollingEnabled}
                onChange={(e) => setPollingEnabled(e.target.checked)}
              />
              <span>Auto-refresh (5s)</span>
            </label>
            {pollingEnabled && <span className="polling-dot">●</span>}
          </div>
        </div>
        <button onClick={fetchNotifications} className="refresh-button" disabled={loading}>
          {loading ? '⟳' : '🔄'} Refresh
        </button>
      </div>

      {notifications.length === 0 ? (
        <p className="empty-state">No notifications found</p>
      ) : (
        <div className="notifications">
          {notifications.map((notification) => (
            <div key={notification.id} className="notification-card">
              <div className="notification-header">
                <h3>
                  {notification.notification_type === 'SMS' ? '📱 ' : '📧 '}
                  {notification.subject || `${notification.notification_type} Notification`}
                </h3>
                <span className={getStatusBadgeClass(notification.status)}>
                  {notification.status}
                </span>
              </div>
              <p className="notification-body">{notification.body}</p>
              <div className="notification-meta">
                <div>
                  <strong>Type:</strong> {notification.notification_type}
                </div>
                <div>
                  <strong>Recipients:</strong> {notification.customer_ids.length} customer(s)
                </div>
                <div>
                  <strong>Created:</strong> {formatDate(notification.created_at)}
                </div>
                <div className="notification-id">
                  <strong>ID:</strong> <code>{notification.id}</code>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotificationList;
