import { useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import './AdminDashboard.css';

export function UsageWidget() {
  const { usage, refreshUsage } = useAuth();

  // Refresh usage each time the widget mounts (e.g. after sending a notification)
  useEffect(() => {
    refreshUsage();
  }, []);

  if (!usage) return null;

  const emailPct = usage.email_limit ? Math.min(100, (usage.email_sent / usage.email_limit) * 100) : 0;
  const smsPct = usage.sms_limit ? Math.min(100, (usage.sms_sent / usage.sms_limit) * 100) : 0;
  const emailAtLimit = usage.email_limit != null && usage.email_sent >= usage.email_limit;
  const smsAtLimit = usage.sms_limit != null && usage.sms_sent >= usage.sms_limit;

  return (
    <div className="usage-widget">
      <div className="usage-widget-title">Your Usage</div>

      <div className="usage-item">
        <div className="usage-item-label">Emails Sent</div>
        <div className={`usage-item-value ${emailAtLimit ? 'at-limit' : ''}`}>
          {usage.email_sent}
          {usage.email_limit != null && ` / ${usage.email_limit}`}
        </div>
        {usage.email_limit != null ? (
          <>
            <div className="usage-item-sub">
              {emailAtLimit ? 'Limit reached' : `${usage.email_remaining} remaining`}
            </div>
            <div className="usage-item-bar-wrap">
              <div
                className="usage-item-bar"
                style={{ width: `${emailPct}%`, background: emailAtLimit ? 'var(--danger)' : 'var(--primary)' }}
              />
            </div>
          </>
        ) : (
          <div className="usage-item-sub">Unlimited</div>
        )}
      </div>

      <div className="usage-item">
        <div className="usage-item-label">SMS Sent</div>
        <div className={`usage-item-value ${smsAtLimit ? 'at-limit' : ''}`}>
          {usage.sms_sent}
          {usage.sms_limit != null && ` / ${usage.sms_limit}`}
        </div>
        {usage.sms_limit != null ? (
          <>
            <div className="usage-item-sub">
              {smsAtLimit ? 'Limit reached' : `${usage.sms_remaining} remaining`}
            </div>
            <div className="usage-item-bar-wrap">
              <div
                className="usage-item-bar"
                style={{ width: `${smsPct}%`, background: smsAtLimit ? 'var(--danger)' : 'var(--success)' }}
              />
            </div>
          </>
        ) : (
          <div className="usage-item-sub">Unlimited</div>
        )}
      </div>
    </div>
  );
}
