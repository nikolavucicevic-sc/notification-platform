/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NotificationStatus } from './NotificationStatus';
import type { NotificationType } from './NotificationType';
export type NotificationResponse = {
    id: string;
    notification_type: NotificationType;
    subject?: (string | null);
    body: string;
    customer_ids: Array<string>;
    status: NotificationStatus;
    created_by_user_id?: (string | null);
    created_at: string;
    updated_at: string;
};

