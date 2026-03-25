import React, { useState, useEffect } from 'react';
import { NotificationCreate, NotificationType } from '../types/notification';
import { notificationApi, customerApi } from '../services/api';
import { Customer } from '../types/customer';
import toast from 'react-hot-toast';

interface NotificationFormProps {
  onSuccess: () => void;
}

const NotificationForm: React.FC<NotificationFormProps> = ({ onSuccess }) => {
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [selectedCustomers, setSelectedCustomers] = useState<string[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setLoadingCustomers(true);
      const data = await customerApi.getCustomers();
      setCustomers(data);
    } catch (error) {
      toast.error('Failed to load customers');
      console.error(error);
    } finally {
      setLoadingCustomers(false);
    }
  };

  const toggleCustomer = (customerId: string) => {
    setSelectedCustomers(prev =>
      prev.includes(customerId)
        ? prev.filter(id => id !== customerId)
        : [...prev, customerId]
    );
  };

  const selectAllCustomers = () => {
    if (selectedCustomers.length === customers.length) {
      setSelectedCustomers([]);
    } else {
      setSelectedCustomers(customers.map(c => c.id));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      if (selectedCustomers.length === 0) {
        setError('Please select at least one customer');
        setLoading(false);
        return;
      }

      const notification: NotificationCreate = {
        notification_type: NotificationType.EMAIL,
        subject,
        body,
        customer_ids: selectedCustomers,
      };

      await notificationApi.createNotification(notification);
      setSuccess(true);
      toast.success('Notification sent successfully!');
      setSubject('');
      setBody('');
      setSelectedCustomers([]);
      onSuccess();
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Failed to send notification';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="notification-form">
      <h2>📧 Send Email Notification</h2>
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <label>Select Recipients ({selectedCustomers.length} selected)</label>
            {customers.length > 0 && (
              <button
                type="button"
                onClick={selectAllCustomers}
                className="select-all-btn"
                style={{
                  width: 'auto',
                  padding: '0.25rem 0.75rem',
                  fontSize: '0.875rem',
                  background: 'transparent',
                  color: 'var(--primary)',
                  border: '1px solid var(--primary)'
                }}
              >
                {selectedCustomers.length === customers.length ? 'Deselect All' : 'Select All'}
              </button>
            )}
          </div>

          {loadingCustomers ? (
            <div style={{ padding: '1rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
              Loading customers...
            </div>
          ) : customers.length === 0 ? (
            <div style={{
              padding: '1rem',
              textAlign: 'center',
              color: 'var(--text-muted)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              background: 'var(--form-bg)'
            }}>
              No customers available. Create customers first in the Customers tab!
            </div>
          ) : (
            <div className="customer-selector">
              {customers.map(customer => (
                <label key={customer.id} className="customer-checkbox">
                  <input
                    type="checkbox"
                    checked={selectedCustomers.includes(customer.id)}
                    onChange={() => toggleCustomer(customer.id)}
                  />
                  <span>
                    {customer.first_name || customer.last_name
                      ? `${customer.first_name || ''} ${customer.last_name || ''}`.trim()
                      : customer.email}
                  </span>
                  <span className="customer-email-small">{customer.email}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">Notification sent successfully!</div>}

        <button type="submit" disabled={loading || customers.length === 0}>
          {loading ? 'Sending...' : 'Send Notification'}
        </button>
      </form>
    </div>
  );
};

export default NotificationForm;
