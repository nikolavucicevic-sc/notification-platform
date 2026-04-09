import { useState, useEffect } from 'react';
import { customerApi } from '../services/api';
import { Customer, CustomerCreate } from '../types/customer';
import toast from 'react-hot-toast';
import './CustomerDashboard.css';

export function CustomerDashboard() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState<CustomerCreate>({
    email: '',
    phone_number: '',
    first_name: '',
    last_name: '',
  });

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const data = await customerApi.getCustomers();
      setCustomers(data);
    } catch (error) {
      toast.error('Failed to load customers');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await customerApi.createCustomer(formData);
      toast.success('Customer created successfully!');
      setShowForm(false);
      setFormData({ email: '', phone_number: '', first_name: '', last_name: '' });
      loadCustomers();
    } catch (error) {
      toast.error('Failed to create customer');
      console.error(error);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this customer?')) return;

    try {
      await customerApi.deleteCustomer(id);
      toast.success('Customer deleted');
      loadCustomers();
    } catch (error) {
      toast.error('Failed to delete customer');
      console.error(error);
    }
  };

  const filteredCustomers = customers.filter(customer =>
    customer.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.first_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    customer.last_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="customer-dashboard">
      <div className="dashboard-header">
        <h2>Customer Management</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? 'Cancel' : '+ Add Customer'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="customer-form">
          <div className="form-grid">
            <input
              type="email"
              placeholder="Email *"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
            <input
              type="tel"
              placeholder="Phone Number (e.g. +1234567890)"
              value={formData.phone_number}
              onChange={(e) => setFormData({ ...formData, phone_number: e.target.value })}
            />
            <input
              type="text"
              placeholder="First Name"
              value={formData.first_name}
              onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
            />
            <input
              type="text"
              placeholder="Last Name"
              value={formData.last_name}
              onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
            />
          </div>
          <button type="submit" className="btn-submit">Create Customer</button>
        </form>
      )}

      <div className="search-bar">
        <input
          type="search"
          placeholder="Search customers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {loading ? (
        <div className="loading">Loading customers...</div>
      ) : (
        <div className="customer-list">
          {filteredCustomers.length === 0 ? (
            <div className="empty-state">
              {searchTerm ? 'No customers found' : 'No customers yet. Create one to get started!'}
            </div>
          ) : (
            filteredCustomers.map(customer => (
              <div key={customer.id} className="customer-card">
                <div className="customer-info">
                  <div className="customer-name">
                    {customer.first_name || customer.last_name
                      ? `${customer.first_name || ''} ${customer.last_name || ''}`.trim()
                      : 'Unnamed Customer'}
                  </div>
                  <div className="customer-email">{customer.email}</div>
                  {customer.phone_number && (
                    <div className="customer-phone">{customer.phone_number}</div>
                  )}
                  <div className="customer-meta">
                    <span className="customer-id">ID: {customer.id.slice(0, 8)}...</span>
                    <span>Created: {new Date(customer.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <div className="customer-actions">
                  <button
                    onClick={() => handleDelete(customer.id)}
                    className="btn-delete"
                    title="Delete customer"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/>
                      <path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
                    </svg>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      <div className="customer-stats">
        <span>Total: {customers.length}</span>
        {searchTerm && <span>Filtered: {filteredCustomers.length}</span>}
      </div>
    </div>
  );
}
