export type TenantCreate = {
    name: string;
    email_limit?: (number | null);
    sms_limit?: (number | null);
    admin_username: string;
    admin_email: string;
    admin_password: string;
    admin_full_name?: (string | null);
};
//# sourceMappingURL=TenantCreate.d.ts.map