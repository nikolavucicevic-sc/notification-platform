import { useState, useEffect } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { scheduleApi, customerApi } from '../services/api';
import { Schedule, ScheduleCreate } from '../types/schedule';
import { Customer } from '../types/customer';
import toast from 'react-hot-toast';
import { format } from 'date-fns';
import './SchedulerUI.css';

export function SchedulerUI() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<ScheduleCreate>({
    schedule_type: 'ONCE',
    scheduled_time: new Date().toISOString(),
    subject: '',
    body: '',
    customer_ids: [],
    notification_type: 'EMAIL',
  });
  const [selectedCustomers, setSelectedCustomers] = useState<string[]>([]);
  const [scheduledDate, setScheduledDate] = useState<Date>(new Date());
  const [endDate, setEndDate] = useState<Date | null>(null);

  useEffect(() => {
    loadSchedules();
    loadCustomers();
  }, []);

  const loadSchedules = async () => {
    try {
      const data = await scheduleApi.getSchedules();
      setSchedules(data);
    } catch (error) {
      toast.error('Failed to load schedules');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadCustomers = async () => {
    try {
      const data = await customerApi.getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Failed to load customers:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (selectedCustomers.length === 0) {
      toast.error('Please select at least one customer');
      return;
    }

    try {
      const scheduleData: ScheduleCreate = {
        ...formData,
        scheduled_time: scheduledDate.toISOString(),
        customer_ids: selectedCustomers,
        recurrence_end_date: endDate?.toISOString(),
      };

      await scheduleApi.createSchedule(scheduleData);
      toast.success('Schedule created successfully!');
      setShowForm(false);
      resetForm();
      loadSchedules();
    } catch (error) {
      toast.error('Failed to create schedule');
      console.error(error);
    }
  };

  const resetForm = () => {
    setFormData({
      schedule_type: 'ONCE',
      scheduled_time: new Date().toISOString(),
      subject: '',
      body: '',
      customer_ids: [],
      notification_type: 'EMAIL',
    });
    setSelectedCustomers([]);
    setScheduledDate(new Date());
    setEndDate(null);
  };

  const handlePause = async (id: string) => {
    try {
      await scheduleApi.pauseSchedule(id);
      toast.success('Schedule paused');
      loadSchedules();
    } catch (error) {
      toast.error('Failed to pause schedule');
    }
  };

  const handleResume = async (id: string) => {
    try {
      await scheduleApi.resumeSchedule(id);
      toast.success('Schedule resumed');
      loadSchedules();
    } catch (error) {
      toast.error('Failed to resume schedule');
    }
  };

  const handleCancel = async (id: string) => {
    if (!confirm('Are you sure you want to cancel this schedule?')) return;

    try {
      await scheduleApi.cancelSchedule(id);
      toast.success('Schedule cancelled');
      loadSchedules();
    } catch (error) {
      toast.error('Failed to cancel schedule');
    }
  };

  const toggleCustomer = (customerId: string) => {
    setSelectedCustomers(prev =>
      prev.includes(customerId)
        ? prev.filter(id => id !== customerId)
        : [...prev, customerId]
    );
  };

  const getStatusBadgeClass = (status: string) => {
    const statusMap: Record<string, string> = {
      SCHEDULED: 'status-pending',
      RUNNING: 'status-processing',
      COMPLETED: 'status-completed',
      FAILED: 'status-failed',
      CANCELLED: 'status-cancelled',
    };
    return statusMap[status] || 'status-pending';
  };

  return (
    <div className="scheduler-ui">
      <div className="scheduler-header">
        <h2>📅 Schedule Notifications</h2>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          {showForm ? 'Cancel' : '+ Create Schedule'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="schedule-form">
          <div className="form-section">
            <h3>Schedule Type</h3>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  name="schedule_type"
                  value="ONCE"
                  checked={formData.schedule_type === 'ONCE'}
                  onChange={(e) => setFormData({ ...formData, schedule_type: e.target.value as 'ONCE' | 'RECURRING' })}
                />
                One-time
              </label>
              <label>
                <input
                  type="radio"
                  name="schedule_type"
                  value="RECURRING"
                  checked={formData.schedule_type === 'RECURRING'}
                  onChange={(e) => setFormData({ ...formData, schedule_type: e.target.value as 'ONCE' | 'RECURRING' })}
                />
                Recurring
              </label>
            </div>
          </div>

          <div className="form-section">
            <h3>Schedule Time</h3>
            <DatePicker
              selected={scheduledDate}
              onChange={(date) => date && setScheduledDate(date)}
              showTimeSelect
              dateFormat="Pp"
              minDate={new Date()}
              className="date-picker"
            />
          </div>

          {formData.schedule_type === 'RECURRING' && (
            <>
              <div className="form-section">
                <h3>Recurrence Pattern</h3>
                <select
                  value={formData.recurrence_type || ''}
                  onChange={(e) => setFormData({ ...formData, recurrence_type: e.target.value as any })}
                  required
                >
                  <option value="">Select pattern...</option>
                  <option value="HOURLY">Hourly</option>
                  <option value="DAILY">Daily</option>
                  <option value="WEEKLY">Weekly</option>
                  <option value="MONTHLY">Monthly</option>
                </select>
              </div>

              <div className="form-section">
                <h3>End Date (Optional)</h3>
                <DatePicker
                  selected={endDate}
                  onChange={(date) => setEndDate(date)}
                  showTimeSelect
                  dateFormat="Pp"
                  minDate={scheduledDate}
                  isClearable
                  placeholderText="No end date"
                  className="date-picker"
                />
              </div>
            </>
          )}

          <div className="form-section">
            <h3>Notification Content</h3>
            <input
              type="text"
              placeholder="Subject *"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              required
            />
            <textarea
              placeholder="Body *"
              value={formData.body}
              onChange={(e) => setFormData({ ...formData, body: e.target.value })}
              rows={4}
              required
            />
          </div>

          <div className="form-section">
            <h3>Select Recipients ({selectedCustomers.length} selected)</h3>
            <div className="customer-selector">
              {customers.length === 0 ? (
                <div className="no-customers">No customers available. Create customers first!</div>
              ) : (
                customers.map(customer => (
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
                ))
              )}
            </div>
          </div>

          <button type="submit" className="btn-submit">Create Schedule</button>
        </form>
      )}

      {loading ? (
        <div className="loading">Loading schedules...</div>
      ) : (
        <div className="schedule-list">
          {schedules.length === 0 ? (
            <div className="empty-state">
              No scheduled notifications yet. Create one to get started!
            </div>
          ) : (
            schedules.map(schedule => (
              <div key={schedule.id} className="schedule-card">
                <div className="schedule-header">
                  <h4>{schedule.subject}</h4>
                  <span className={`status-badge ${getStatusBadgeClass(schedule.status)}`}>
                    {schedule.status}
                  </span>
                </div>

                <div className="schedule-body">{schedule.body}</div>

                <div className="schedule-meta">
                  <div className="meta-row">
                    <span>📅 Scheduled: {format(new Date(schedule.scheduled_time), 'PPp')}</span>
                    <span>🔄 Type: {schedule.schedule_type}</span>
                  </div>
                  {schedule.recurrence_type && (
                    <div className="meta-row">
                      <span>🔁 Recurrence: {schedule.recurrence_type}</span>
                      <span>▶️ Run Count: {schedule.run_count}</span>
                    </div>
                  )}
                  {schedule.next_run && (
                    <div className="meta-row">
                      <span>⏭️ Next Run: {format(new Date(schedule.next_run), 'PPp')}</span>
                    </div>
                  )}
                  <div className="meta-row">
                    <span>👥 Recipients: {schedule.customer_ids.length}</span>
                    <span>{schedule.is_active ? '✅ Active' : '⏸️ Paused'}</span>
                  </div>
                </div>

                <div className="schedule-actions">
                  {schedule.is_active ? (
                    <button onClick={() => handlePause(schedule.id)} className="btn-action">
                      ⏸️ Pause
                    </button>
                  ) : (
                    <button onClick={() => handleResume(schedule.id)} className="btn-action">
                      ▶️ Resume
                    </button>
                  )}
                  <button onClick={() => handleCancel(schedule.id)} className="btn-danger-action">
                    ❌ Cancel
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
