import { useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface Tenant {
  id: string;
  name: string;
  email_limit: number | null;
  sms_limit: number | null;
  email_sent: number;
  sms_sent: number;
  is_active: boolean;
  created_at: string;
  user_count: number;
}

interface CreateTenantForm {
  name: string;
  email_limit: string;
  sms_limit: string;
  admin_username: string;
  admin_email: string;
  admin_password: string;
  admin_full_name: string;
}

const emptyForm: CreateTenantForm = {
  name: '',
  email_limit: '',
  sms_limit: '',
  admin_username: '',
  admin_email: '',
  admin_password: '',
  admin_full_name: '',
};

export function TenantsDashboard() {
  const [tenants, setTenants] = useState<Tenant[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState<CreateTenantForm>(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [editingLimits, setEditingLimits] = useState<string | null>(null);
  const [limitForm, setLimitForm] = useState({ email_limit: '', sms_limit: '' });

  const fetchTenants = async () => {
    try {
      const res = await axios.get('/api/tenants');
      setTenants(Array.isArray(res.data) ? res.data : []);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to load tenants');
      setTenants([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTenants(); }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await axios.post('/api/tenants', {
        name: form.name,
        email_limit: form.email_limit ? parseInt(form.email_limit) : null,
        sms_limit: form.sms_limit ? parseInt(form.sms_limit) : null,
        admin_username: form.admin_username,
        admin_email: form.admin_email,
        admin_password: form.admin_password,
        admin_full_name: form.admin_full_name || null,
      });
      toast.success(`Tenant "${form.name}" created`);
      setForm(emptyForm);
      setShowCreate(false);
      fetchTenants();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Failed to create tenant');
    } finally {
      setSubmitting(false);
    }
  };

  const toggleActive = async (tenant: Tenant) => {
    try {
      await axios.patch(`/api/tenants/${tenant.id}`, { is_active: !tenant.is_active });
      toast.success(`Tenant ${tenant.is_active ? 'deactivated' : 'activated'}`);
      fetchTenants();
    } catch {
      toast.error('Failed to update tenant');
    }
  };

  const saveLimits = async (tenantId: string) => {
    try {
      await axios.patch(`/api/tenants/${tenantId}`, {
        email_limit: limitForm.email_limit !== '' ? parseInt(limitForm.email_limit) : null,
        sms_limit: limitForm.sms_limit !== '' ? parseInt(limitForm.sms_limit) : null,
      });
      toast.success('Limits updated');
      setEditingLimits(null);
      fetchTenants();
    } catch {
      toast.error('Failed to update limits');
    }
  };

  const startEditLimits = (tenant: Tenant) => {
    setEditingLimits(tenant.id);
    setLimitForm({
      email_limit: tenant.email_limit !== null ? String(tenant.email_limit) : '',
      sms_limit: tenant.sms_limit !== null ? String(tenant.sms_limit) : '',
    });
  };

  if (loading) return <div className="loading-screen"><div className="loading-spinner" /></div>;

  return (
    <div className="admin-dashboard">
      <div className="admin-header">
        <div>
          <h2>Tenants</h2>
          <p className="admin-subtitle">{tenants.length} company{tenants.length !== 1 ? 'ies' : ''} registered</p>
        </div>
        <button className="btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? 'Cancel' : '+ New Tenant'}
        </button>
      </div>

      {showCreate && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '1rem' }}>Create New Tenant</h3>
          <form onSubmit={handleCreate}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div className="form-group">
                <label className="form-label">Company Name *</label>
                <input className="form-input" required value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Admin Full Name</label>
                <input className="form-input" value={form.admin_full_name}
                  onChange={e => setForm(f => ({ ...f, admin_full_name: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Admin Username *</label>
                <input className="form-input" required value={form.admin_username}
                  onChange={e => setForm(f => ({ ...f, admin_username: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Admin Email *</label>
                <input className="form-input" type="email" required value={form.admin_email}
                  onChange={e => setForm(f => ({ ...f, admin_email: e.target.value }))} />
              </div>
              <div className="form-group">
                <label className="form-label">Admin Password *</label>
                <input className="form-input" type="password" required minLength={8} value={form.admin_password}
                  onChange={e => setForm(f => ({ ...f, admin_password: e.target.value }))} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                <div className="form-group">
                  <label className="form-label">Email Limit</label>
                  <input className="form-input" type="number" min="0" placeholder="Unlimited" value={form.email_limit}
                    onChange={e => setForm(f => ({ ...f, email_limit: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label className="form-label">SMS Limit</label>
                  <input className="form-input" type="number" min="0" placeholder="Unlimited" value={form.sms_limit}
                    onChange={e => setForm(f => ({ ...f, sms_limit: e.target.value }))} />
                </div>
              </div>
            </div>
            <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem' }}>
              <button type="submit" className="btn-primary" disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Tenant'}
              </button>
              <button type="button" className="btn-secondary" onClick={() => { setShowCreate(false); setForm(emptyForm); }}>
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {tenants.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            No tenants yet. Create your first tenant above.
          </div>
        )}
        {tenants.map(tenant => (
          <div key={tenant.id} className="card" style={{ opacity: tenant.is_active ? 1 : 0.6 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.25rem' }}>
                  <h3 style={{ margin: 0 }}>{tenant.name}</h3>
                  <span className={`status-badge status-${tenant.is_active ? 'completed' : 'failed'}`}>
                    {tenant.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', margin: 0 }}>
                  {tenant.user_count} user{tenant.user_count !== 1 ? 's' : ''} · Created {new Date(tenant.created_at).toLocaleDateString()}
                </p>
              </div>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button className="btn-secondary" onClick={() => startEditLimits(tenant)}>Edit Limits</button>
                <button
                  className={tenant.is_active ? 'btn-danger' : 'btn-secondary'}
                  onClick={() => toggleActive(tenant)}
                >
                  {tenant.is_active ? 'Deactivate' : 'Activate'}
                </button>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginTop: '1rem' }}>
              <div className="stat-card">
                <div className="stat-label">Email Sent</div>
                <div className="stat-value">{tenant.email_sent.toLocaleString()}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Email Limit</div>
                <div className="stat-value">{tenant.email_limit !== null ? tenant.email_limit.toLocaleString() : '∞'}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">SMS Sent</div>
                <div className="stat-value">{tenant.sms_sent.toLocaleString()}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">SMS Limit</div>
                <div className="stat-value">{tenant.sms_limit !== null ? tenant.sms_limit.toLocaleString() : '∞'}</div>
              </div>
            </div>

            {tenant.email_limit !== null && (
              <div style={{ marginTop: '0.75rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                  <span>Email usage</span>
                  <span>{Math.round((tenant.email_sent / tenant.email_limit) * 100)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${Math.min(100, (tenant.email_sent / tenant.email_limit) * 100)}%` }} />
                </div>
              </div>
            )}
            {tenant.sms_limit !== null && (
              <div style={{ marginTop: '0.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                  <span>SMS usage</span>
                  <span>{Math.round((tenant.sms_sent / tenant.sms_limit) * 100)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${Math.min(100, (tenant.sms_sent / tenant.sms_limit) * 100)}%` }} />
                </div>
              </div>
            )}

            {editingLimits === tenant.id && (
              <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--bg-secondary)', borderRadius: '8px' }}>
                <h4 style={{ margin: '0 0 0.75rem' }}>Update Limits</h4>
                <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label">Email Limit</label>
                    <input className="form-input" type="number" min="0" placeholder="Unlimited"
                      value={limitForm.email_limit}
                      onChange={e => setLimitForm(f => ({ ...f, email_limit: e.target.value }))} />
                  </div>
                  <div className="form-group" style={{ margin: 0 }}>
                    <label className="form-label">SMS Limit</label>
                    <input className="form-input" type="number" min="0" placeholder="Unlimited"
                      value={limitForm.sms_limit}
                      onChange={e => setLimitForm(f => ({ ...f, sms_limit: e.target.value }))} />
                  </div>
                  <button className="btn-primary" onClick={() => saveLimits(tenant.id)}>Save</button>
                  <button className="btn-secondary" onClick={() => setEditingLimits(null)}>Cancel</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
