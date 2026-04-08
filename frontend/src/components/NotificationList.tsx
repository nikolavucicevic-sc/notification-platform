import React, { useEffect, useState, useRef, useCallback } from 'react';
import { Notification, NotificationStatus, NotificationType } from '../types/notification';
import { notificationApi } from '../services/api';
import { usePolling } from '../hooks/usePolling';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

interface NotificationListProps {
  refreshTrigger: number;
}

type SortOrder = 'newest' | 'oldest';
type StatusFilter = 'ALL' | NotificationStatus;

const NotificationList: React.FC<NotificationListProps> = ({ refreshTrigger }) => {
  const { user, isAdmin } = useAuth();

  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-refresh
  const [pollingEnabled, setPollingEnabled] = useState(true);
  const [pollSeconds, setPollSeconds] = useState(5);
  const pollInputRef = useRef<HTMLInputElement>(null);

  // Expand/collapse
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  // Filters
  const [typeTab, setTypeTab] = useState<'ALL' | NotificationType>('ALL');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('ALL');
  const [userFilter, setUserFilter] = useState<string>('ALL');
  const [sortOrder, setSortOrder] = useState<SortOrder>('newest');

  const previousStatuses = useRef<Map<string, NotificationStatus>>(new Map());

  const toggleExpand = (id: string) => {
    setExpandedIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handlePollBlur = () => {
    const n = parseInt(pollInputRef.current?.value ?? '');
    const valid = !isNaN(n) && n >= 5 ? n : 5;
    setPollSeconds(valid);
    if (pollInputRef.current) pollInputRef.current.value = String(valid);
  };

  const fetchNotifications = useCallback(async () => {
    if (!loading) setLoading(true);
    setError(null);
    try {
      const data = await notificationApi.getNotifications();

      data.forEach(n => {
        const prev = previousStatuses.current.get(n.id);
        if (prev && prev !== n.status) {
          if (n.status === NotificationStatus.COMPLETED)
            toast.success(`"${n.subject || 'Notification'}" completed!`);
          else if (n.status === NotificationStatus.FAILED)
            toast.error(`"${n.subject || 'Notification'}" failed`);
          else if (n.status === NotificationStatus.PROCESSING)
            toast.loading(`Processing "${n.subject || 'notification'}"...`, { duration: 2000 });
        }
        previousStatuses.current.set(n.id, n.status);
      });

      setNotifications(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch notifications');
      toast.error('Failed to refresh notifications');
    } finally {
      setLoading(false);
    }
  }, []);

  usePolling(fetchNotifications, pollSeconds * 1000, pollingEnabled);

  useEffect(() => { fetchNotifications(); }, [refreshTrigger]);

  // Derived: unique senders for user filter dropdown (admin only)
  const uniqueSenders = Array.from(
    new Set(notifications.map(n => n.created_by_user_id).filter(Boolean) as string[])
  );

  // Apply filters + sort
  const visible = notifications
    .filter(n => typeTab === 'ALL' || n.notification_type === typeTab)
    .filter(n => statusFilter === 'ALL' || n.status === statusFilter)
    .filter(n => userFilter === 'ALL' || n.created_by_user_id === userFilter)
    .sort((a, b) => {
      const diff = new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      return sortOrder === 'newest' ? diff : -diff;
    });

  const getStatusBadgeClass = (status: NotificationStatus) => {
    switch (status) {
      case NotificationStatus.COMPLETED:  return 'status-badge status-completed';
      case NotificationStatus.PROCESSING: return 'status-badge status-processing';
      case NotificationStatus.PENDING:    return 'status-badge status-pending';
      case NotificationStatus.FAILED:     return 'status-badge status-failed';
      default: return 'status-badge';
    }
  };

  const formatDate = (d: string) => new Date(d).toLocaleString();

  const emailCount = notifications.filter(n => n.notification_type === NotificationType.EMAIL).length;
  const smsCount   = notifications.filter(n => n.notification_type === NotificationType.SMS).length;

  if (error && notifications.length === 0) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <div className="notification-list">

      {/* ── Header ── */}
      <div className="list-header">
        <div>
          <h2>Notifications</h2>
          <div className="polling-indicator">
            <label>
              <input
                type="checkbox"
                checked={pollingEnabled}
                onChange={e => setPollingEnabled(e.target.checked)}
              />
              Auto-refresh
            </label>
            {pollingEnabled && (
              <>
                <span className="polling-dot" />
                <input
                  ref={pollInputRef}
                  type="number"
                  className="poll-interval-input"
                  defaultValue={pollSeconds}
                  min={5}
                  onBlur={handlePollBlur}
                  title="Refresh interval in seconds (min 5)"
                />
                <span className="poll-interval-label">s</span>
              </>
            )}
          </div>
        </div>
        <button onClick={fetchNotifications} className="refresh-button" disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* ── Type tabs ── */}
      <div className="notif-type-tabs">
        <button
          className={`notif-type-tab ${typeTab === 'ALL' ? 'active' : ''}`}
          onClick={() => setTypeTab('ALL')}
        >
          All <span className="tab-count">{notifications.length}</span>
        </button>
        <button
          className={`notif-type-tab ${typeTab === NotificationType.EMAIL ? 'active' : ''}`}
          onClick={() => setTypeTab(NotificationType.EMAIL)}
        >
          Email <span className="tab-count">{emailCount}</span>
        </button>
        <button
          className={`notif-type-tab ${typeTab === NotificationType.SMS ? 'active' : ''}`}
          onClick={() => setTypeTab(NotificationType.SMS)}
        >
          SMS <span className="tab-count">{smsCount}</span>
        </button>
      </div>

      {/* ── Filter bar ── */}
      <div className="notif-filter-bar">
        <select
          className="notif-filter-select"
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value as StatusFilter)}
        >
          <option value="ALL">All statuses</option>
          <option value={NotificationStatus.PENDING}>Pending</option>
          <option value={NotificationStatus.PROCESSING}>Processing</option>
          <option value={NotificationStatus.COMPLETED}>Completed</option>
          <option value={NotificationStatus.FAILED}>Failed</option>
        </select>

        {isAdmin && uniqueSenders.length > 0 && (
          <select
            className="notif-filter-select"
            value={userFilter}
            onChange={e => setUserFilter(e.target.value)}
          >
            <option value="ALL">All users</option>
            {uniqueSenders.map(id => (
              <option key={id} value={id}>
                {id === user?.id ? 'You' : id.substring(0, 8) + '...'}
              </option>
            ))}
          </select>
        )}

        <button
          className="notif-sort-btn"
          onClick={() => setSortOrder(o => o === 'newest' ? 'oldest' : 'newest')}
          title="Toggle sort order"
        >
          {sortOrder === 'newest' ? '↓ Newest first' : '↑ Oldest first'}
        </button>

        <span className="notif-filter-count">
          {visible.length} of {notifications.length}
        </span>
      </div>

      {/* ── List ── */}
      {visible.length === 0 ? (
        <p className="empty-state">
          {notifications.length === 0 ? 'No notifications yet' : 'No notifications match the current filters'}
        </p>
      ) : (
        <div className="notifications">
          {visible.map(notification => {
            const expanded = expandedIds.has(notification.id);
            const isOwn = notification.created_by_user_id === user?.id;
            return (
              <div key={notification.id} className={`notification-card ${expanded ? 'expanded' : 'collapsed'}`}>
                <div className="notification-header" onClick={() => toggleExpand(notification.id)}>
                  <div className="notification-header-left">
                    <span className="notification-chevron">{expanded ? '▾' : '▸'}</span>
                    <h3>{notification.subject || `${notification.notification_type} Notification`}</h3>
                  </div>
                  <div className="notification-header-right">
                    {isAdmin && !isOwn && notification.created_by_user_id && (
                      <span className="notif-user-badge" title={notification.created_by_user_id}>
                        {notification.created_by_user_id.substring(0, 6)}…
                      </span>
                    )}
                    <span className="notification-type-badge">{notification.notification_type}</span>
                    <span className={getStatusBadgeClass(notification.status)}>{notification.status}</span>
                  </div>
                </div>
                {expanded && (
                  <>
                    <p className="notification-body">{notification.body}</p>
                    <div className="notification-meta">
                      <div><strong>Recipients:</strong> {notification.customer_ids.length} customer(s)</div>
                      <div><strong>Created:</strong> {formatDate(notification.created_at)}</div>
                      {notification.created_by_user_id && (
                        <div><strong>Sent by:</strong> {isOwn ? 'You' : notification.created_by_user_id}</div>
                      )}
                      <div className="notification-id"><strong>ID:</strong> <code>{notification.id}</code></div>
                    </div>
                  </>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default NotificationList;
