import React, { useState, useEffect } from 'react';
import { NotificationCreate, NotificationType } from '../types/notification';
import { notificationApi, customerApi, templateApi } from '../services/api';
import { Customer } from '../types/customer';
import { Template } from '../types/template';
import toast from 'react-hot-toast';

interface NotificationFormProps {
  onSuccess: () => void;
}

const NotificationForm: React.FC<NotificationFormProps> = ({ onSuccess }) => {
  const [notificationType, setNotificationType] = useState<NotificationType>(NotificationType.EMAIL);
  const [useTemplate, setUseTemplate] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [templateVariables, setTemplateVariables] = useState<Record<string, string>>({});

  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [selectedCustomers, setSelectedCustomers] = useState<string[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingCustomers, setLoadingCustomers] = useState(true);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  useEffect(() => {
    if (useTemplate) {
      loadTemplates();
    }
  }, [useTemplate, notificationType]);

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

  const loadTemplates = async () => {
    try {
      setLoadingTemplates(true);
      const data = await templateApi.getTemplates(notificationType);
      setTemplates(data);
    } catch (error) {
      toast.error('Failed to load templates');
      console.error(error);
    } finally {
      setLoadingTemplates(false);
    }
  };

  const handleTemplateSelect = (templateId: string) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setSelectedTemplate(template);
      // Initialize variables with empty strings
      const vars: Record<string, string> = {};
      template.variables.forEach(v => {
        vars[v] = '';
      });
      setTemplateVariables(vars);
    } else {
      setSelectedTemplate(null);
      setTemplateVariables({});
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

  const renderTemplate = (text: string, vars: Record<string, string>): string => {
    let rendered = text;
    Object.keys(vars).forEach(key => {
      const regex = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
      rendered = rendered.replace(regex, vars[key] || `{{${key}}}`);
    });
    return rendered;
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

      let finalSubject = subject;
      let finalBody = body;

      if (useTemplate && selectedTemplate) {
        // Check if all required variables are filled
        const missingVars = selectedTemplate.variables.filter(v => !templateVariables[v]);
        if (missingVars.length > 0) {
          setError(`Please fill in all variables: ${missingVars.join(', ')}`);
          setLoading(false);
          return;
        }

        // Render template with variables
        finalSubject = selectedTemplate.subject ? renderTemplate(selectedTemplate.subject, templateVariables) : '';
        finalBody = renderTemplate(selectedTemplate.body, templateVariables);
      } else {
        // Manual mode validation
        if (notificationType === NotificationType.EMAIL && !subject) {
          setError('Please fill in subject for email');
          setLoading(false);
          return;
        }
        if (!body) {
          setError('Please fill in message body');
          setLoading(false);
          return;
        }
      }

      const notification: NotificationCreate = {
        notification_type: notificationType,
        subject: notificationType === NotificationType.EMAIL ? finalSubject : undefined,
        body: finalBody,
        customer_ids: selectedCustomers,
      };

      await notificationApi.createNotification(notification);
      setSuccess(true);
      toast.success('Notification sent successfully!');

      // Reset form
      setSubject('');
      setBody('');
      setSelectedCustomers([]);
      setSelectedTemplate(null);
      setTemplateVariables({});
      setUseTemplate(false);

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
      <h2>Send Notification</h2>
      <form onSubmit={handleSubmit}>
        {/* Notification Type Selection */}
        <div className="form-group">
          <label htmlFor="notificationType">Notification Type</label>
          <select
            id="notificationType"
            value={notificationType}
            onChange={(e) => {
              setNotificationType(e.target.value as NotificationType);
              setSelectedTemplate(null);
              setTemplateVariables({});
              setUseTemplate(false);
            }}
          >
            <option value={NotificationType.EMAIL}>Email</option>
            <option value={NotificationType.SMS}>SMS</option>
          </select>
        </div>

        {/* Template Toggle */}
        <div className="form-group">
          <label className="template-toggle">
            <input
              type="checkbox"
              checked={useTemplate}
              onChange={(e) => setUseTemplate(e.target.checked)}
            />
            <span>Use a template</span>
          </label>
        </div>

        {useTemplate ? (
          <>
            {/* Template Selection */}
            <div className="form-group">
              <label htmlFor="template">Select Template</label>
              {loadingTemplates ? (
                <div style={{ padding: '1rem', color: 'var(--text-secondary)' }}>
                  Loading templates...
                </div>
              ) : templates.length === 0 ? (
                <div style={{
                  padding: '1rem',
                  textAlign: 'center',
                  color: 'var(--text-muted)',
                  border: '1px solid var(--border)',
                  borderRadius: '6px',
                  background: 'var(--form-bg)'
                }}>
                  No templates available. Create one in the Templates tab!
                </div>
              ) : (
                <select
                  id="template"
                  value={selectedTemplate?.id || ''}
                  onChange={(e) => handleTemplateSelect(e.target.value)}
                  required
                >
                  <option value="">-- Select a template --</option>
                  {templates.map(template => (
                    <option key={template.id} value={template.id}>
                      {template.name} ({template.variables.length} variables)
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Template Variables */}
            {selectedTemplate && selectedTemplate.variables.length > 0 && (
              <div className="form-group">
                <label>Fill in Template Variables</label>
                <div className="variable-inputs">
                  {selectedTemplate.variables.map(varName => (
                    <div key={varName} className="variable-input-group">
                      <label htmlFor={`var-${varName}`}>
                        <code>{`{{${varName}}}`}</code>
                      </label>
                      <input
                        type="text"
                        id={`var-${varName}`}
                        value={templateVariables[varName] || ''}
                        onChange={(e) => setTemplateVariables({
                          ...templateVariables,
                          [varName]: e.target.value
                        })}
                        placeholder={`Enter ${varName}`}
                        required
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Template Preview */}
            {selectedTemplate && Object.keys(templateVariables).length > 0 && (
              <div className="template-preview">
                <strong>Preview:</strong>
                {selectedTemplate.subject && (
                  <div className="preview-section">
                    <span className="preview-label">Subject:</span>
                    <div className="preview-content">
                      {renderTemplate(selectedTemplate.subject, templateVariables)}
                    </div>
                  </div>
                )}
                <div className="preview-section">
                  <span className="preview-label">Body:</span>
                  <div className="preview-content">
                    {renderTemplate(selectedTemplate.body, templateVariables)}
                  </div>
                </div>
              </div>
            )}
          </>
        ) : (
          <>
            {/* Manual Input Mode */}
            {notificationType === NotificationType.EMAIL && (
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
            )}

            <div className="form-group">
              <label htmlFor="body">{notificationType === NotificationType.EMAIL ? 'Body' : 'Message'}</label>
              <textarea
                id="body"
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder={notificationType === NotificationType.EMAIL ? 'Enter email body' : 'Enter SMS message'}
                rows={6}
                required
              />
            </div>
          </>
        )}

        {/* Customer Selection */}
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
                  <span className="customer-name-text">
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

        <button type="submit" disabled={loading || customers.length === 0 || (useTemplate && templates.length === 0)}>
          {loading ? 'Sending...' : 'Send Notification'}
        </button>
      </form>
    </div>
  );
};

export default NotificationForm;
