/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TenantCreate } from '../models/TenantCreate';
import type { TenantResponse } from '../models/TenantResponse';
import type { TenantUpdate } from '../models/TenantUpdate';
import type { UserResponse } from '../models/UserResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class TenantsService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * List Tenants
     * List all tenants with user counts. SUPER_ADMIN only.
     * @returns TenantResponse Successful Response
     * @throws ApiError
     */
    public listTenantsTenantsGet(): CancelablePromise<Array<TenantResponse>> {
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
    public createTenantTenantsPost(
        requestBody: TenantCreate,
    ): CancelablePromise<TenantResponse> {
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
    public listTenantsTenantsGet1(): CancelablePromise<Array<TenantResponse>> {
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
    public createTenantTenantsPost1(
        requestBody: TenantCreate,
    ): CancelablePromise<TenantResponse> {
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
    public getTenantTenantsTenantIdGet(
        tenantId: string,
    ): CancelablePromise<TenantResponse> {
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
    public updateTenantTenantsTenantIdPatch(
        tenantId: string,
        requestBody: TenantUpdate,
    ): CancelablePromise<TenantResponse> {
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
    public listTenantUsersTenantsTenantIdUsersGet(
        tenantId: string,
    ): CancelablePromise<Array<UserResponse>> {
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
