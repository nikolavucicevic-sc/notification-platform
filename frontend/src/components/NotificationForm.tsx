import React, { useState } from 'react';
import { NotificationCreate, NotificationType } from '../types/notification';
import { notificationApi } from '../services/api';

interface NotificationFormProps {
  onSuccess: () => void;
}

const NotificationForm: React.FC<NotificationFormProps> = ({ onSuccess }) => {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [customerIds, setCustomerIds] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const customerIdArray = customerIds
        .split(',')
        .map(id => id.trim())
        .filter(id => id.length > 0);

      if (customerIdArray.length === 0) {
        setError('Please enter at least one customer ID');
        setLoading(false);
        return;
      }

      const notification: NotificationCreate = {
        notification_type: NotificationType.EMAIL,
        subject,
        body,
        customer_ids: customerIdArray,
      };

      await notificationApi.createNotification(notification);
      setSuccess(true);
      setSubject('');
      setBody('');
      setCustomerIds('');
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to send notification');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="notification-form">
      <h2>Send Email Notification</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="subject">Subject</label>
          <input
            type="text"
            id="subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            placeholder="Enter email subject"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="body">Body</label>
          <textarea
            id="body"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Enter email body"
            rows={6}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="customerIds">Customer IDs (comma-separated UUIDs)</label>
          <input
            type="text"
            id="customerIds"
            value={customerIds}
            onChange={(e) => setCustomerIds(e.target.value)}
            placeholder="e.g., 123e4567-e89b-12d3-a456-426614174000, ..."
            required
          />
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">Notification sent successfully!</div>}

        <button type="submit" disabled={loading}>
          {loading ? 'Sending...' : 'Send Notification'}
        </button>
      </form>
    </div>
  );
};

export default NotificationForm;
