/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NotificationType } from './NotificationType';
export type NotificationCreate = {
    notification_type: NotificationType;
    subject?: (string | null);
    body: string;
    customer_ids: Array<string>;
};

