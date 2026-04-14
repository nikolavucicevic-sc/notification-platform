import type { UserRole } from './UserRole';
export type UserCreate = {
    email: string;
    username: string;
    password: string;
    full_name?: (string | null);
    role?: UserRole;
};
//# sourceMappingURL=UserCreate.d.ts.map