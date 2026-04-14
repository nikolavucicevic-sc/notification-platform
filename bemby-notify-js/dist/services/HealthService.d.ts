import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export declare class HealthService {
    readonly httpRequest: BaseHttpRequest;
    constructor(httpRequest: BaseHttpRequest);
    /**
     * Health Check
     * Health check endpoint that verifies:
     * - API is responding
     * - Database connection is working
     * - Redis connection is working
     * - Queue depths
     * @returns any Successful Response
     * @throws ApiError
     */
    healthCheckHealthGet(): CancelablePromise<any>;
    /**
     * Readiness Check
     * Readiness probe for Kubernetes/Docker health checks.
     * Returns 200 if service is ready to accept traffic.
     * @returns any Successful Response
     * @throws ApiError
     */
    readinessCheckHealthReadyGet(): CancelablePromise<any>;
    /**
     * Liveness Check
     * Liveness probe for Kubernetes/Docker health checks.
     * Returns 200 if service is alive (even if not fully ready).
     * @returns any Successful Response
     * @throws ApiError
     */
    livenessCheckHealthLiveGet(): CancelablePromise<any>;
}
//# sourceMappingURL=HealthService.d.ts.map