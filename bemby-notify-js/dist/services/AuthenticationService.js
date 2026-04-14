"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.AuthenticationService = void 0;
class AuthenticationService {
    constructor(httpRequest) {
        this.httpRequest = httpRequest;
    }
    /**
     * Login
     * @param requestBody
     * @returns Token Successful Response
     * @throws ApiError
     */
    loginAuthLoginPost(requestBody) {
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
    listUsersAuthUsersGet() {
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
    createUserAuthUsersPost(requestBody) {
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
    getCurrentUserInfoAuthMeGet() {
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
    updateMyProfileAuthMePatch(requestBody) {
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
    updateUserAuthUsersUserIdPatch(userId, requestBody) {
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
    updateUserRoleAuthUsersUserIdRolePut(userId, requestBody) {
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
    getMyUsageAuthUsersMeUsageGet() {
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
    updateUserLimitsAuthUsersUserIdLimitsPatch(userId, requestBody) {
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
    listApiKeysAuthApiKeysGet() {
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
    createApiKeyAuthApiKeysPost(requestBody) {
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
    deleteApiKeyAuthApiKeysKeyIdDelete(keyId) {
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
    listAuditLogsAuthAuditLogsGet(limit = 100) {
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
exports.AuthenticationService = AuthenticationService;
//# sourceMappingURL=AuthenticationService.js.map