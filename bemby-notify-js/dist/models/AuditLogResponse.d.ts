export type AuditLogResponse = {
    id: string;
    user_id: (string | null);
    action: string;
    resource_type: (string | null);
    resource_id: (string | null);
    details: (Record<string, any> | null);
    ip_address: (string | null);
    user_agent: (string | null);
    created_at: string;
};
//# sourceMappingURL=AuditLogResponse.d.ts.map