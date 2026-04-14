/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { NotificationCreate } from '../models/NotificationCreate';
import type { NotificationResponse } from '../models/NotificationResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class NotificationsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Get Notifications
     * Get notifications. SUPER_ADMIN sees all. Others see only their tenant's notifications.
     * @returns NotificationResponse Successful Response
     * @throws ApiError
     */
    public getNotificationsNotificationsGet(): CancelablePromise<Array<NotificationResponse>> {
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
    public createNotificationNotificationsPost(
        requestBody: NotificationCreate,
    ): CancelablePromise<NotificationResponse> {
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
    public updateNotificationStatusNotificationsNotificationIdStatusPatch(
        notificationId: string,
        requestBody: Record<string, any>,
    ): CancelablePromise<NotificationResponse> {
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
    public getNotificationNotificationsNotificationIdGet(
        notificationId: string,
    ): CancelablePromise<NotificationResponse> {
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
