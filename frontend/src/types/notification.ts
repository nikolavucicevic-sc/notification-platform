export enum NotificationType {
  EMAIL = 'EMAIL'
}

export enum NotificationStatus {
  PENDING = 'PENDING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED'
}

export interface NotificationCreate {
  notification_type: NotificationType;
  subject: string;
  body: string;
  customer_ids: string[];
}

export interface Notification {
  id: string;
  notification_type: NotificationType;
  subject: string;
  body: string;
  customer_ids: string[];
  status: NotificationStatus;
  created_at: string;
  updated_at: string;
}
