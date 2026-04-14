"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.HealthService = void 0;
class HealthService {
    constructor(httpRequest) {
        this.httpRequest = httpRequest;
    }
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
    healthCheckHealthGet() {
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
    readinessCheckHealthReadyGet() {
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
    livenessCheckHealthLiveGet() {
        return this.httpRequest.request({
            method: 'GET',
            url: '/health/live',
        });
    }
}
exports.HealthService = HealthService;
//# sourceMappingURL=HealthService.js.map