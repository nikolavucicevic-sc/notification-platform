import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export declare class DlqService {
    readonly httpRequest: BaseHttpRequest;
    constructor(httpRequest: BaseHttpRequest);
    /**
     * Get Dlq Messages
     * Get all messages from Dead Letter Queues (both email and SMS).
     * Returns failed notifications for review and manual retry.
     * @returns any Successful Response
     * @throws ApiError
     */
    getDlqMessagesDlqGet(): CancelablePromise<any>;
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
    retryDlqMessageDlqRetryChannelNotificationIdPost(channel: string, notificationId: string): CancelablePromise<any>;
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
    clearDlqDlqClearChannelDelete(channel: string): CancelablePromise<any>;
}
//# sourceMappingURL=DlqService.d.ts.map