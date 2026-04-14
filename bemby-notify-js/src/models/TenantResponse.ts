/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type TenantResponse = {
    id: string;
    name: string;
    email_limit: (number | null);
    sms_limit: (number | null);
    email_sent: number;
    sms_sent: number;
    is_active: boolean;
    created_at: string;
    user_count?: (number | null);
};

