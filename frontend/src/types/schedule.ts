export interface Schedule {
  id: string;
  schedule_type: 'ONCE' | 'RECURRING';
  scheduled_time: string;
  recurrence_type?: 'HOURLY' | 'DAILY' | 'WEEKLY' | 'MONTHLY';
  recurrence_end_date?: string;
  notification_type: string;
  subject: string;
  body: string;
  customer_ids: string[];
  status: 'SCHEDULED' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CANCELLED';
  job_id?: string;
  last_run?: string;
  next_run?: string;
  run_count: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  created_by?: string;
}

export interface ScheduleCreate {
  schedule_type: 'ONCE' | 'RECURRING';
  scheduled_time: string;
  recurrence_type?: 'HOURLY' | 'DAILY' | 'WEEKLY' | 'MONTHLY';
  recurrence_end_date?: string;
  notification_type?: string;
  subject: string;
  body: string;
  customer_ids: string[];
  created_by?: string;
}
