import type { TenantCreate } from '../models/TenantCreate';
import type { TenantResponse } from '../models/TenantResponse';
import type { TenantUpdate } from '../models/TenantUpdate';
import type { UserResponse } from '../models/UserResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export declare class TenantsService {
    readonly httpRequest: BaseHttpRequest;
    constructor(httpRequest: BaseHttpRequest);
    /**
     * List Tenants
     * List all tenants with user counts. SUPER_ADMIN only.
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    listTenantsTenantsGet(): CancelablePromise<Array<TenantResponse>>;
    /**
     * Create Tenant
     * Create a new tenant and their first admin account. SUPER_ADMIN only.
     * @param requestBody
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    createTenantTenantsPost(requestBody: TenantCreate): CancelablePromise<TenantResponse>;
    /**
     * List Tenants
     * List all tenants with user counts. SUPER_ADMIN only.
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    listTenantsTenantsGet1(): CancelablePromise<Array<TenantResponse>>;
    /**
     * Create Tenant
     * Create a new tenant and their first admin account. SUPER_ADMIN only.
     * @param requestBody
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    createTenantTenantsPost1(requestBody: TenantCreate): CancelablePromise<TenantResponse>;
    /**
     * Get Tenant
     * Get a single tenant. SUPER_ADMIN only.
     * @param tenantId
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    getTenantTenantsTenantIdGet(tenantId: string): CancelablePromise<TenantResponse>;
    /**
     * Update Tenant
     * Update tenant name, limits, or active status. SUPER_ADMIN only.
     * @param tenantId
     * @param requestBody
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    updateTenantTenantsTenantIdPatch(tenantId: string, requestBody: TenantUpdate): CancelablePromise<TenantResponse>;
    /**
     * List Tenant Users
     * List all users in a tenant. SUPER_ADMIN only.
     * @param tenantId
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    listTenantUsersTenantsTenantIdUsersGet(tenantId: string): CancelablePromise<Array<UserResponse>>;
}
//# sourceMappingURL=TenantsService.d.ts.map