"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.DefaultService = void 0;
class DefaultService {
    constructor(httpRequest) {
        this.httpRequest = httpRequest;
    }
    /**
     * Metrics
     * Prometheus metrics endpoint for monitoring.
     * @returns any Successful Response
     * @throws ApiError
     */
    metricsMetricsGet() {
        return this.httpRequest.request({
            method: 'GET',
            url: '/metrics',
        });
    }
}
exports.DefaultService = DefaultService;
//# sourceMappingURL=DefaultService.js.map