"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.TenantsService = void 0;
class TenantsService {
    constructor(httpRequest) {
        this.httpRequest = httpRequest;
    }
    /**
     * List Tenants
     * List all tenants with user counts. SUPER_ADMIN only.
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    listTenantsTenantsGet() {
        return this.httpRequest.request({
            method: 'GET',
            url: '/tenants',
        });
    }
    /**
     * Create Tenant
     * Create a new tenant and their first admin account. SUPER_ADMIN only.
     * @param requestBody
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    createTenantTenantsPost(requestBody) {
        return this.httpRequest.request({
            method: 'POST',
            url: '/tenants',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Tenants
     * List all tenants with user counts. SUPER_ADMIN only.
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    listTenantsTenantsGet1() {
        return this.httpRequest.request({
            method: 'GET',
            url: '/tenants/',
        });
    }
    /**
     * Create Tenant
     * Create a new tenant and their first admin account. SUPER_ADMIN only.
     * @param requestBody
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    createTenantTenantsPost1(requestBody) {
        return this.httpRequest.request({
            method: 'POST',
            url: '/tenants/',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Tenant
     * Get a single tenant. SUPER_ADMIN only.
     * @param tenantId
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    getTenantTenantsTenantIdGet(tenantId) {
        return this.httpRequest.request({
            method: 'GET',
            url: '/tenants/{tenant_id}',
            path: {
                'tenant_id': tenantId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Tenant
     * Update tenant name, limits, or active status. SUPER_ADMIN only.
     * @param tenantId
     * @param requestBody
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    updateTenantTenantsTenantIdPatch(tenantId, requestBody) {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/tenants/{tenant_id}',
            path: {
                'tenant_id': tenantId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Tenant Users
     * List all users in a tenant. SUPER_ADMIN only.
     * @param tenantId
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    listTenantUsersTenantsTenantIdUsersGet(tenantId) {
        return this.httpRequest.request({
            method: 'GET',
            url: '/tenants/{tenant_id}/users',
            path: {
                'tenant_id': tenantId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
exports.TenantsService = TenantsService;
//# sourceMappingURL=TenantsService.js.map