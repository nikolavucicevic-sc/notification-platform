/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { AxiosHttpRequest } from './core/AxiosHttpRequest';
import { AuthenticationService } from './services/AuthenticationService';
import { DefaultService } from './services/DefaultService';
import { DlqService } from './services/DlqService';
import { HealthService } from './services/HealthService';
import { NotificationsService } from './services/NotificationsService';
import { TenantsService } from './services/TenantsService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class BembyNotifyClient {
    public readonly authentication: AuthenticationService;
    public readonly default: DefaultService;
    public readonly dlq: DlqService;
    public readonly health: HealthService;
    public readonly notifications: NotificationsService;
    public readonly tenants: TenantsService;
    public readonly request: BaseHttpRequest;
    constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = AxiosHttpRequest) {
        this.request = new HttpRequest({
            BASE: config?.BASE ?? '',
            VERSION: config?.VERSION ?? '2.0.0',
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? 'include',
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });
        this.authentication = new AuthenticationService(this.request);
        this.default = new DefaultService(this.request);
        this.dlq = new DlqService(this.request);
        this.health = new HealthService(this.request);
        this.notifications = new NotificationsService(this.request);
        this.tenants = new TenantsService(this.request);
    }
}

