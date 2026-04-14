/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { UserRole } from './UserRole';
export type UserCreate = {
    email: string;
    username: string;
    password: string;
    full_name?: (string | null);
    role?: UserRole;
};

