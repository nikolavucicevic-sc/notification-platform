/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class HealthService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
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
    public healthCheckHealthGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/health',
        });
    }
    /**
     * Readiness Check
     * Readiness probe for Kubernetes/Docker health checks.
     * Returns 200 if service is ready to accept traffic.
     * @returns any Successful Response
     * @throws ApiError
     */
    public readinessCheckHealthReadyGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/health/ready',
        });
    }
    /**
     * Liveness Check
     * Liveness probe for Kubernetes/Docker health checks.
     * Returns 200 if service is alive (even if not fully ready).
     * @returns any Successful Response
     * @throws ApiError
     */
    public livenessCheckHealthLiveGet(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/health/live',
        });
    }
}
