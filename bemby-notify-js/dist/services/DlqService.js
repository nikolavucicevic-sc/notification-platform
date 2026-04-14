"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DlqService = void 0;
class DlqService {
    constructor(httpRequest) {
        this.httpRequest = httpRequest;
    }
    /**
     * Get Dlq Messages
     * Get all messages from Dead Letter Queues (both email and SMS).
     * Returns failed notifications for review and manual retry.
     * @returns any Successful Response
     * @throws ApiError
     */
    getDlqMessagesDlqGet() {
        return this.httpRequest.request({
            method: 'GET',
            url: '/dlq',
        });
    }
    /**
     * Retry Dlq Message
     * Retry a specific failed notification by moving it back to the main queue.
     *
     * Args:
     * channel: "email" or "sms"
     * notification_id: The notification ID to retry
     *
     * Requires: OPERATOR or ADMIN role
     * @param channel
     * @param notificationId
     * @returns any Successful Response
     * @throws ApiError
     */
    retryDlqMessageDlqRetryChannelNotificationIdPost(channel, notificationId) {
        return this.httpRequest.request({
            method: 'POST',
            url: '/dlq/retry/{channel}/{notification_id}',
            path: {
                'channel': channel,
                'notification_id': notificationId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Clear Dlq
     * Clear all messages from a specific DLQ (email or sms).
     *
     * Args:
     * channel: "email" or "sms"
     *
     * Requires: ADMIN role
     * @param channel
     * @returns any Successful Response
     * @throws ApiError
     */
    clearDlqDlqClearChannelDelete(channel) {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/dlq/clear/{channel}',
            path: {
                'channel': channel,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
exports.DlqService = DlqService;
//# sourceMappingURL=DlqService.js.map