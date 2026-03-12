import React, { useEffect, useState } from 'react';
import { Notification, NotificationStatus } from '../types/notification';
import { notificationApi } from '../services/api';

interface NotificationListProps {
  refreshTrigger: number;
}

const NotificationList: React.FC<NotificationListProps> = ({ refreshTrigger }) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await notificationApi.getNotifications();
      setNotifications(data.sort((a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      ));
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch notifications');
    } finally {
      setLoading(false);
    }
  };

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

  if (loading) {
    return <div className="loading">Loading notifications...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="notification-list">
      <div className="list-header">
        <h2>Notifications</h2>
        <button onClick={fetchNotifications} className="refresh-button">
          Refresh
        </button>
      </div>

      {notifications.length === 0 ? (
        <p className="empty-state">No notifications found</p>
      ) : (
        <div className="notifications">
          {notifications.map((notification) => (
            <div key={notification.id} className="notification-card">
              <div className="notification-header">
                <h3>{notification.subject}</h3>
                <span className={getStatusBadgeClass(notification.status)}>
                  {notification.status}
                </span>
              </div>
              <p className="notification-body">{notification.body}</p>
              <div className="notification-meta">
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
