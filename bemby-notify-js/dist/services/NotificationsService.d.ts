import type { NotificationCreate } from '../models/NotificationCreate';
import type { NotificationResponse } from '../models/NotificationResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export declare class NotificationsService {
    readonly httpRequest: BaseHttpRequest;
    constructor(httpRequest: BaseHttpRequest);
    /**
     * Get Notifications
     * Get notifications. SUPER_ADMIN sees all. Others see only their tenant's notifications.
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    getNotificationsNotificationsGet(): CancelablePromise<Array<NotificationResponse>>;
    /**
     * Create Notification
     * @param requestBody
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    createNotificationNotificationsPost(requestBody: NotificationCreate): CancelablePromise<NotificationResponse>;
    /**
     * Update Notification Status
     * Internal endpoint — called by email-sender/sms-sender. No auth required.
     * @param notificationId
     * @param requestBody
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    updateNotificationStatusNotificationsNotificationIdStatusPatch(notificationId: string, requestBody: Record<string, any>): CancelablePromise<NotificationResponse>;
    /**
     * Get Notification
     * @param notificationId
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    getNotificationNotificationsNotificationIdGet(notificationId: string): CancelablePromise<NotificationResponse>;
}
//# sourceMappingURL=NotificationsService.d.ts.map