import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export declare class DefaultService {
    readonly httpRequest: BaseHttpRequest;
    constructor(httpRequest: BaseHttpRequest);
    /**
     * Metrics
     * Prometheus metrics endpoint for monitoring.
     * @returns any Successful Response
     * @throws ApiError
     */
    metricsMetricsGet(): CancelablePromise<any>;
}
//# sourceMappingURL=DefaultService.d.ts.map