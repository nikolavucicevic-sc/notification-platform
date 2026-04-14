import type { NotificationType } from './NotificationType';
export type NotificationCreate = {
    notification_type: NotificationType;
    subject?: (string | null);
    body: string;
    customer_ids: Array<string>;
};
//# sourceMappingURL=NotificationCreate.d.ts.map