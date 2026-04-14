/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
export type UserResponse = {
    id: string;
    email: string;
    username: string;
    full_name: (string | null);
    role: UserRole;
    is_active: boolean;
    created_at: string;
    last_login: (string | null);
    tenant_id: (string | null);
    email_limit: (number | null);
    sms_limit: (number | null);
    email_sent: number;
    sms_sent: number;
};

