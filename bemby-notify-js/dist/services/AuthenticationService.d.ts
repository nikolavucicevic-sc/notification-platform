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
export declare class AuthenticationService {
    readonly httpRequest: BaseHttpRequest;
    constructor(httpRequest: BaseHttpRequest);
    /**
     * Login
     * @param requestBody
     * @returns Token Successful Response
     * @throws ApiError
     */
    loginAuthLoginPost(requestBody: UserLogin): CancelablePromise<Token>;
    /**
     * List Users
     * List users. Tenant admins see only their own tenant's users.
     * SUPER_ADMIN sees all users.
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    listUsersAuthUsersGet(): CancelablePromise<Array<UserResponse>>;
    /**
     * Create User
     * Create a user within the current admin's tenant.
     * Tenant admins can create OPERATOR and VIEWER only.
     * SUPER_ADMIN cannot use this endpoint (use POST /tenants instead).
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    createUserAuthUsersPost(requestBody: UserCreate): CancelablePromise<UserResponse>;
    /**
     * Get Current User Info
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    getCurrentUserInfoAuthMeGet(): CancelablePromise<UserResponse>;
    /**
     * Update My Profile
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    updateMyProfileAuthMePatch(requestBody: ProfileUpdate): CancelablePromise<UserResponse>;
    /**
     * Update User
     * @param userId
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    updateUserAuthUsersUserIdPatch(userId: string, requestBody: UserUpdate): CancelablePromise<UserResponse>;
    /**
     * Update User Role
     * @param userId
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    updateUserRoleAuthUsersUserIdRolePut(userId: string, requestBody: Record<string, any>): CancelablePromise<UserResponse>;
    /**
     * Get My Usage
     * @returns UserUsageResponse Successful Response
     * @throws ApiError
     */
    getMyUsageAuthUsersMeUsageGet(): CancelablePromise<UserUsageResponse>;
    /**
     * Update User Limits
     * @param userId
     * @param requestBody
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    updateUserLimitsAuthUsersUserIdLimitsPatch(userId: string, requestBody: UserLimitsUpdate): CancelablePromise<UserResponse>;
    /**
     * List Api Keys
     * @returns APIKeyResponse Successful Response
     * @throws ApiError
     */
    listApiKeysAuthApiKeysGet(): CancelablePromise<Array<APIKeyResponse>>;
    /**
     * Create Api Key
     * @param requestBody
     * @returns APIKeyCreateResponse Successful Response
     * @throws ApiError
     */
    createApiKeyAuthApiKeysPost(requestBody: APIKeyCreate): CancelablePromise<APIKeyCreateResponse>;
    /**
     * Delete Api Key
     * @param keyId
     * @returns void
     * @throws ApiError
     */
    deleteApiKeyAuthApiKeysKeyIdDelete(keyId: string): CancelablePromise<void>;
    /**
     * List Audit Logs
     * Audit logs scoped to tenant. SUPER_ADMIN sees all.
     * @param limit
     * @returns AuditLogResponse Successful Response
     * @throws ApiError
     */
    listAuditLogsAuthAuditLogsGet(limit?: number): CancelablePromise<Array<AuditLogResponse>>;
}
//# sourceMappingURL=AuthenticationService.d.ts.map