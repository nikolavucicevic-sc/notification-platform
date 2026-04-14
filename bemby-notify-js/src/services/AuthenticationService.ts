/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { APIKeyCreate } from '../models/APIKeyCreate';
import type { APIKeyCreateResponse } from '../models/APIKeyCreateResponse';
import type { APIKeyResponse } from '../models/APIKeyResponse';
import type { AuditLogResponse } from '../models/AuditLogResponse';
import type { ProfileUpdate } from '../models/ProfileUpdate';
import type { Token } from '../models/Token';
import type { UserCreate } from '../models/UserCreate';
import type { UserLimitsUpdate } from '../models/UserLimitsUpdate';
import type { UserLogin } from '../models/UserLogin';
import type { UserResponse } from '../models/UserResponse';
import type { UserUpdate } from '../models/UserUpdate';
import type { UserUsageResponse } from '../models/UserUsageResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuthenticationService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Login
     * @param requestBody
     * @returns Token Successful Response
     * @throws ApiError
     */
    public loginAuthLoginPost(
        requestBody: UserLogin,
    ): CancelablePromise<Token> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Users
     * List users. Tenant admins see only their own tenant's users.
     * SUPER_ADMIN sees all users.
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public listUsersAuthUsersGet(): CancelablePromise<Array<UserResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/auth/users',
        });
    }
    /**
     * Create User
     * Create a user within the current admin's tenant.
     * Tenant admins can create OPERATOR and VIEWER only.
     * SUPER_ADMIN cannot use this endpoint (use POST /tenants instead).
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public createUserAuthUsersPost(
        requestBody: UserCreate,
    ): CancelablePromise<UserResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/auth/users',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Current User Info
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public getCurrentUserInfoAuthMeGet(): CancelablePromise<UserResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/auth/me',
        });
    }
    /**
     * Update My Profile
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public updateMyProfileAuthMePatch(
        requestBody: ProfileUpdate,
    ): CancelablePromise<UserResponse> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/auth/me',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update User
     * @param userId
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public updateUserAuthUsersUserIdPatch(
        userId: string,
        requestBody: UserUpdate,
    ): CancelablePromise<UserResponse> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/auth/users/{user_id}',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update User Role
     * @param userId
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public updateUserRoleAuthUsersUserIdRolePut(
        userId: string,
        requestBody: Record<string, any>,
    ): CancelablePromise<UserResponse> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/auth/users/{user_id}/role',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get My Usage
     * @returns UserUsageResponse Successful Response
     * @throws ApiError
     */
    public getMyUsageAuthUsersMeUsageGet(): CancelablePromise<UserUsageResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/auth/users/me/usage',
        });
    }
    /**
     * Update User Limits
     * @param userId
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public updateUserLimitsAuthUsersUserIdLimitsPatch(
        userId: string,
        requestBody: UserLimitsUpdate,
    ): CancelablePromise<UserResponse> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/auth/users/{user_id}/limits',
            path: {
                'user_id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Api Keys
     * @returns APIKeyResponse Successful Response
     * @throws ApiError
     */
    public listApiKeysAuthApiKeysGet(): CancelablePromise<Array<APIKeyResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/auth/api-keys',
        });
    }
    /**
     * Create Api Key
     * @param requestBody
     * @returns APIKeyCreateResponse Successful Response
     * @throws ApiError
     */
    public createApiKeyAuthApiKeysPost(
        requestBody: APIKeyCreate,
    ): CancelablePromise<APIKeyCreateResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/auth/api-keys',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Api Key
     * @param keyId
     * @returns void
     * @throws ApiError
     */
    public deleteApiKeyAuthApiKeysKeyIdDelete(
        keyId: string,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/auth/api-keys/{key_id}',
            path: {
                'key_id': keyId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * List Audit Logs
     * Audit logs scoped to tenant. SUPER_ADMIN sees all.
     * @param limit
     * @returns AuditLogResponse Successful Response
     * @throws ApiError
     */
    public listAuditLogsAuthAuditLogsGet(
        limit: number = 100,
    ): CancelablePromise<Array<AuditLogResponse>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/auth/audit-logs',
            query: {
                'limit': limit,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
