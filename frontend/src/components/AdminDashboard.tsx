import { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import './AdminDashboard.css';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: 'ADMIN' | 'OPERATOR' | 'VIEWER';
  is_active: boolean;
  created_at: string;
  last_login: string | null;
  email_limit: number | null;
  sms_limit: number | null;
  email_sent: number;
  sms_sent: number;
}

interface APIKey {
  id: string;
  key_name: string;
  key_prefix: string;
  is_active: boolean;
  created_at: string;
  last_used_at: string | null;
  expires_at: string | null;
}

interface AuditLog {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  details: any;
  ip_address: string | null;
  user_agent: string | null;
  created_at: string;
}

export function AdminDashboard() {
  const { user: currentUser, isAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState<'users' | 'limits' | 'api-keys' | 'audit'>('users');

  // Users
  const [users, setUsers] = useState<User[]>([]);
  const [loadingUsers, setLoadingUsers] = useState(false);

  // Limits editing state: userId -> { email_limit, sms_limit }
  const [editingLimits, setEditingLimits] = useState<Record<string, { email: string; sms: string }>>({});

  // API Keys
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [loadingKeys, setLoadingKeys] = useState(false);
  const [showNewKeyModal, setShowNewKeyModal] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyDays, setNewKeyDays] = useState('');
  const [createdKey, setCreatedKey] = useState<string | null>(null);

  // Audit Logs
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loadingAudit, setLoadingAudit] = useState(false);

  useEffect(() => {
    if (activeTab === 'users') fetchUsers();
    if (activeTab === 'limits') fetchUsers();
    if (activeTab === 'api-keys') fetchAPIKeys();
    if (activeTab === 'audit') fetchAuditLogs();
  }, [activeTab]);

  const fetchUsers = async () => {
    setLoadingUsers(true);
    try {
      const response = await axios.get('/api/auth/users');
      setUsers(response.data);
      // Init editing state for limits tab
      const init: Record<string, { email: string; sms: string }> = {};
      response.data.forEach((u: User) => {
        init[u.id] = {
          email: u.email_limit != null ? String(u.email_limit) : '',
          sms: u.sms_limit != null ? String(u.sms_limit) : '',
        };
      });
      setEditingLimits(init);
    } catch {
      toast.error('Failed to load users');
    } finally {
      setLoadingUsers(false);
    }
  };

  const fetchAPIKeys = async () => {
    setLoadingKeys(true);
    try {
      const response = await axios.get('/api/auth/api-keys');
      setApiKeys(response.data);
    } catch {
      toast.error('Failed to load API keys');
    } finally {
      setLoadingKeys(false);
    }
  };

  const fetchAuditLogs = async () => {
    setLoadingAudit(true);
    try {
      const response = await axios.get('/api/auth/audit-logs?limit=100');
      setAuditLogs(response.data);
    } catch {
      toast.error('Failed to load audit logs');
    } finally {
      setLoadingAudit(false);
    }
  };

  const createAPIKey = async () => {
    try {
      const payload: any = { key_name: newKeyName };
      if (newKeyDays) payload.expires_in_days = parseInt(newKeyDays);
      const response = await axios.post('/api/auth/api-keys', payload);
      setCreatedKey(response.data.api_key);
      toast.success("API key created! Save it now - it won't be shown again!");
      fetchAPIKeys();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to create API key');
    }
  };

  const deleteAPIKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to delete this API key?')) return;
    try {
      await axios.delete(`/api/auth/api-keys/${keyId}`);
      toast.success('API key deleted');
      fetchAPIKeys();
    } catch {
      toast.error('Failed to delete API key');
    }
  };

  const updateUserRole = async (userId: string, newRole: 'ADMIN' | 'OPERATOR' | 'VIEWER') => {
    if (!confirm(`Are you sure you want to change this user's role to ${newRole}?`)) return;
    try {
      await axios.put(`/api/auth/users/${userId}/role`, { role: newRole });
      toast.success('User role updated successfully');
      fetchUsers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update user role');
    }
  };

  const saveLimits = async (userId: string) => {
    const vals = editingLimits[userId];
    const payload: any = {};
    payload.email_limit = vals.email.trim() !== '' ? parseInt(vals.email) : null;
    payload.sms_limit = vals.sms.trim() !== '' ? parseInt(vals.sms) : null;

    try {
      await axios.patch(`/api/auth/users/${userId}/limits`, payload);
      toast.success('Limits updated');
      fetchUsers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update limits');
    }
  };

  const getRoleBadgeClass = (role: string) => {
    switch (role) {
      case 'ADMIN': return 'role-badge role-admin';
      case 'OPERATOR': return 'role-badge role-operator';
      case 'VIEWER': return 'role-badge role-viewer';
      default: return 'role-badge';
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'Never';
    return new Date(dateString).toLocaleString();
  };

  if (!isAdmin) {
    return (
      <div className="admin-dashboard">
        <div className="access-denied">
          <h2>Access Denied</h2>
          <p>Admin access required to view this page.</p>
          <p>Your role: <span className={getRoleBadgeClass(currentUser?.role || '')}>{currentUser?.role}</span></p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h2>Admin Dashboard</h2>
        <p>Manage users, limits, API keys, and view audit logs</p>
      </div>

      <div className="admin-tabs">
        <button className={`admin-tab ${activeTab === 'users' ? 'active' : ''}`} onClick={() => setActiveTab('users')}>Users</button>
        <button className={`admin-tab ${activeTab === 'limits' ? 'active' : ''}`} onClick={() => setActiveTab('limits')}>Usage &amp; Limits</button>
        <button className={`admin-tab ${activeTab === 'api-keys' ? 'active' : ''}`} onClick={() => setActiveTab('api-keys')}>API Keys</button>
        <button className={`admin-tab ${activeTab === 'audit' ? 'active' : ''}`} onClick={() => setActiveTab('audit')}>Audit Logs</button>
      </div>

      <div className="admin-content">
        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="users-section">
            <div className="section-header">
              <h3>User Management</h3>
              <button className="btn-primary">+ Add User</button>
            </div>

            {loadingUsers ? (
              <p>Loading users...</p>
            ) : (
              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Full Name</th>
                      <th>Role</th>
                      <th>Status</th>
                      <th>Last Login</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td><strong>{user.username}</strong></td>
                        <td>{user.email}</td>
                        <td>{user.full_name || '-'}</td>
                        <td><span className={getRoleBadgeClass(user.role)}>{user.role}</span></td>
                        <td>
                          <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                            {user.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td>{formatDate(user.last_login)}</td>
                        <td>
                          {user.id !== currentUser?.id ? (
                            <select
                              className="role-select"
                              value={user.role}
                              onChange={(e) => updateUserRole(user.id, e.target.value as 'ADMIN' | 'OPERATOR' | 'VIEWER')}
                            >
                              <option value="VIEWER">VIEWER</option>
                              <option value="OPERATOR">OPERATOR</option>
                              <option value="ADMIN">ADMIN</option>
                            </select>
                          ) : (
                            <span className="text-muted">You</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Usage & Limits Tab */}
        {activeTab === 'limits' && (
          <div className="users-section">
            <div className="section-header">
              <h3>Usage &amp; Limits</h3>
              <button className="btn-secondary" onClick={fetchUsers}>Refresh</button>
            </div>
            <p className="limits-hint">Set per-user sending limits. Leave blank for unlimited. Admins are never limited.</p>

            {loadingUsers ? (
              <p>Loading...</p>
            ) : (
              <div className="users-table">
                <table>
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Role</th>
                      <th>Emails Sent</th>
                      <th>Email Limit</th>
                      <th>SMS Sent</th>
                      <th>SMS Limit</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((user) => (
                      <tr key={user.id}>
                        <td><strong>{user.username}</strong></td>
                        <td><span className={getRoleBadgeClass(user.role)}>{user.role}</span></td>
                        <td>
                          <span className="usage-count">{user.email_sent}</span>
                          {user.email_limit != null && (
                            <span className="usage-bar-wrap">
                              <span
                                className="usage-bar"
                                style={{ width: `${Math.min(100, (user.email_sent / user.email_limit) * 100)}%`, background: user.email_sent >= user.email_limit ? 'var(--danger)' : 'var(--primary)' }}
                              />
                            </span>
                          )}
                        </td>
                        <td>
                          <input
                            className="limit-input"
                            type="number"
                            min="0"
                            placeholder="Unlimited"
                            value={editingLimits[user.id]?.email ?? ''}
                            onChange={(e) => setEditingLimits(prev => ({
                              ...prev,
                              [user.id]: { ...prev[user.id], email: e.target.value }
                            }))}
                          />
                        </td>
                        <td>
                          <span className="usage-count">{user.sms_sent}</span>
                          {user.sms_limit != null && (
                            <span className="usage-bar-wrap">
                              <span
                                className="usage-bar"
                                style={{ width: `${Math.min(100, (user.sms_sent / user.sms_limit) * 100)}%`, background: user.sms_sent >= user.sms_limit ? 'var(--danger)' : 'var(--success)' }}
                              />
                            </span>
                          )}
                        </td>
                        <td>
                          <input
                            className="limit-input"
                            type="number"
                            min="0"
                            placeholder="Unlimited"
                            value={editingLimits[user.id]?.sms ?? ''}
                            onChange={(e) => setEditingLimits(prev => ({
                              ...prev,
                              [user.id]: { ...prev[user.id], sms: e.target.value }
                            }))}
                          />
                        </td>
                        <td>
                          <button className="btn-primary btn-small" onClick={() => saveLimits(user.id)}>
                            Save
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* API Keys Tab */}
        {activeTab === 'api-keys' && (
          <div className="api-keys-section">
            <div className="section-header">
              <h3>API Key Management</h3>
              <button className="btn-primary" onClick={() => setShowNewKeyModal(true)}>+ Create API Key</button>
            </div>

            {showNewKeyModal && (
              <div className="modal-overlay" onClick={() => { setShowNewKeyModal(false); setCreatedKey(null); }}>
                <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                  {createdKey ? (
                    <div className="key-created">
                      <h3>API Key Created</h3>
                      <p className="warning-text">Save this key now. It won't be shown again.</p>
                      <div className="api-key-display">
                        <code>{createdKey}</code>
                        <button onClick={() => { navigator.clipboard.writeText(createdKey); toast.success('Copied to clipboard!'); }}>Copy</button>
                      </div>
                      <button className="btn-primary" onClick={() => { setShowNewKeyModal(false); setCreatedKey(null); setNewKeyName(''); setNewKeyDays(''); }}>Done</button>
                    </div>
                  ) : (
                    <div className="create-key-form">
                      <h3>Create New API Key</h3>
                      <div className="form-group">
                        <label>Key Name</label>
                        <input type="text" value={newKeyName} onChange={(e) => setNewKeyName(e.target.value)} placeholder="e.g., Production API" />
                      </div>
                      <div className="form-group">
                        <label>Expires In (days, optional)</label>
                        <input type="number" value={newKeyDays} onChange={(e) => setNewKeyDays(e.target.value)} placeholder="Leave empty for no expiration" />
                      </div>
                      <div className="modal-actions">
                        <button className="btn-secondary" onClick={() => setShowNewKeyModal(false)}>Cancel</button>
                        <button className="btn-primary" onClick={createAPIKey} disabled={!newKeyName}>Create Key</button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {loadingKeys ? <p>Loading API keys...</p> : apiKeys.length === 0 ? (
              <div className="empty-state"><p>No API keys yet. Create one to get started!</p></div>
            ) : (
              <div className="keys-table">
                <table>
                  <thead>
                    <tr>
                      <th>Name</th><th>Prefix</th><th>Created</th><th>Last Used</th><th>Expires</th><th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {apiKeys.map((key) => (
                      <tr key={key.id}>
                        <td><strong>{key.key_name}</strong></td>
                        <td><code>{key.key_prefix}...</code></td>
                        <td>{formatDate(key.created_at)}</td>
                        <td>{formatDate(key.last_used_at)}</td>
                        <td>{formatDate(key.expires_at)}</td>
                        <td><button className="btn-danger-small" onClick={() => deleteAPIKey(key.id)}>Delete</button></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* Audit Logs Tab */}
        {activeTab === 'audit' && (
          <div className="audit-section">
            <div className="section-header">
              <h3>Audit Logs (Last 100)</h3>
              <button className="btn-secondary" onClick={fetchAuditLogs}>Refresh</button>
            </div>

            {loadingAudit ? <p>Loading audit logs...</p> : (
              <div className="audit-table">
                <table>
                  <thead>
                    <tr><th>Time</th><th>Action</th><th>Resource</th><th>IP Address</th><th>Details</th></tr>
                  </thead>
                  <tbody>
                    {auditLogs.map((log) => (
                      <tr key={log.id}>
                        <td>{formatDate(log.created_at)}</td>
                        <td><code>{log.action}</code></td>
                        <td>
                          {log.resource_type && (
                            <span>{log.resource_type}{log.resource_id && <><br/><small>{log.resource_id.substring(0, 8)}...</small></>}</span>
                          )}
                        </td>
                        <td>{log.ip_address || '-'}</td>
                        <td>{log.details && <small><pre>{JSON.stringify(log.details, null, 2)}</pre></small>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
