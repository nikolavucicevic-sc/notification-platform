"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NotificationsService = void 0;
class NotificationsService {
    constructor(httpRequest) {
        this.httpRequest = httpRequest;
    }
    /**
     * Get Notifications
     * Get notifications. SUPER_ADMIN sees all. Others see only their tenant's notifications.
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    getNotificationsNotificationsGet() {
        return this.httpRequest.request({
            method: 'GET',
            url: '/notifications',
        });
    }
    /**
     * Create Notification
     * @param requestBody
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    createNotificationNotificationsPost(requestBody) {
        return this.httpRequest.request({
            method: 'POST',
            url: '/notifications',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Notification Status
     * Internal endpoint — called by email-sender/sms-sender. No auth required.
     * @param notificationId
     * @param requestBody
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    updateNotificationStatusNotificationsNotificationIdStatusPatch(notificationId, requestBody) {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/notifications/{notification_id}/status',
            path: {
                'notification_id': notificationId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Notification
     * @param notificationId
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    getNotificationNotificationsNotificationIdGet(notificationId) {
        return this.httpRequest.request({
            method: 'GET',
            url: '/notifications/{notification_id}',
            path: {
                'notification_id': notificationId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
exports.NotificationsService = NotificationsService;
//# sourceMappingURL=NotificationsService.js.map