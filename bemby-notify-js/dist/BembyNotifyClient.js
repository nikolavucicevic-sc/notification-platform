"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.BembyNotifyClient = void 0;
const AxiosHttpRequest_1 = require("./core/AxiosHttpRequest");
const AuthenticationService_1 = require("./services/AuthenticationService");
const DefaultService_1 = require("./services/DefaultService");
const DlqService_1 = require("./services/DlqService");
const HealthService_1 = require("./services/HealthService");
const NotificationsService_1 = require("./services/NotificationsService");
const TenantsService_1 = require("./services/TenantsService");
class BembyNotifyClient {
    constructor(config, HttpRequest = AxiosHttpRequest_1.AxiosHttpRequest) {
        var _a, _b, _c, _d;
        this.request = new HttpRequest({
            BASE: (_a = config === null || config === void 0 ? void 0 : config.BASE) !== null && _a !== void 0 ? _a : '',
            VERSION: (_b = config === null || config === void 0 ? void 0 : config.VERSION) !== null && _b !== void 0 ? _b : '2.0.0',
            WITH_CREDENTIALS: (_c = config === null || config === void 0 ? void 0 : config.WITH_CREDENTIALS) !== null && _c !== void 0 ? _c : false,
            CREDENTIALS: (_d = config === null || config === void 0 ? void 0 : config.CREDENTIALS) !== null && _d !== void 0 ? _d : 'include',
            TOKEN: config === null || config === void 0 ? void 0 : config.TOKEN,
            USERNAME: config === null || config === void 0 ? void 0 : config.USERNAME,
            PASSWORD: config === null || config === void 0 ? void 0 : config.PASSWORD,
            HEADERS: config === null || config === void 0 ? void 0 : config.HEADERS,
            ENCODE_PATH: config === null || config === void 0 ? void 0 : config.ENCODE_PATH,
        });
        this.authentication = new AuthenticationService_1.AuthenticationService(this.request);
        this.default = new DefaultService_1.DefaultService(this.request);
        this.dlq = new DlqService_1.DlqService(this.request);
        this.health = new HealthService_1.HealthService(this.request);
        this.notifications = new NotificationsService_1.NotificationsService(this.request);
        this.tenants = new TenantsService_1.TenantsService(this.request);
    }
}
exports.BembyNotifyClient = BembyNotifyClient;
//# sourceMappingURL=BembyNotifyClient.js.map