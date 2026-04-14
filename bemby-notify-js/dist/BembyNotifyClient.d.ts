import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { AuthenticationService } from './services/AuthenticationService';
import { DefaultService } from './services/DefaultService';
import { DlqService } from './services/DlqService';
import { HealthService } from './services/HealthService';
import { NotificationsService } from './services/NotificationsService';
import { TenantsService } from './services/TenantsService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export declare class BembyNotifyClient {
    readonly authentication: AuthenticationService;
    readonly default: DefaultService;
    readonly dlq: DlqService;
    readonly health: HealthService;
    readonly notifications: NotificationsService;
    readonly tenants: TenantsService;
    readonly request: BaseHttpRequest;
    constructor(config?: Partial<OpenAPIConfig>, HttpRequest?: HttpRequestConstructor);
}
export {};
//# sourceMappingURL=BembyNotifyClient.d.ts.map