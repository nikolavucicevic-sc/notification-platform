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
//# sourceMappingURL=TenantResponse.d.ts.map