import axios from 'axios';
import { Notification, NotificationCreate } from '../types/notification';
import { Customer, CustomerCreate } from '../types/customer';
import { Schedule, ScheduleCreate } from '../types/schedule';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Notification API
export const notificationApi = {
  createNotification: async (notification: NotificationCreate): Promise<Notification> => {
    const response = await api.post<Notification>('/notifications/', notification);
    return response.data;
  },

  getNotifications: async (): Promise<Notification[]> => {
    const response = await api.get<Notification[]>('/notifications/');
    return response.data;
  },

  getNotification: async (id: string): Promise<Notification> => {
    const response = await api.get<Notification>(`/notifications/${id}`);
    return response.data;
  },
};

// Customer API
export const customerApi = {
  getCustomers: async (): Promise<Customer[]> => {
    const response = await api.get<Customer[]>('/customers/');
    return response.data;
  },

  getCustomer: async (id: string): Promise<Customer> => {
    const response = await api.get<Customer>(`/customers/${id}`);
    return response.data;
  },

  createCustomer: async (customer: CustomerCreate): Promise<Customer> => {
    const response = await api.post<Customer>('/customers/', customer);
    return response.data;
  },

  updateCustomer: async (id: string, customer: Partial<CustomerCreate>): Promise<Customer> => {
    const response = await api.put<Customer>(`/customers/${id}`, customer);
    return response.data;
  },

  deleteCustomer: async (id: string): Promise<void> => {
    await api.delete(`/customers/${id}`);
  },
};

// Schedule API
export const scheduleApi = {
  getSchedules: async (): Promise<Schedule[]> => {
    const response = await api.get<Schedule[]>('/schedules/');
    return response.data;
  },

  getSchedule: async (id: string): Promise<Schedule> => {
    const response = await api.get<Schedule>(`/schedules/${id}`);
    return response.data;
  },

  createSchedule: async (schedule: ScheduleCreate): Promise<Schedule> => {
    const response = await api.post<Schedule>('/schedules/', schedule);
    return response.data;
  },

  updateSchedule: async (id: string, schedule: Partial<ScheduleCreate>): Promise<Schedule> => {
    const response = await api.put<Schedule>(`/schedules/${id}`, schedule);
    return response.data;
  },

  cancelSchedule: async (id: string): Promise<void> => {
    await api.delete(`/schedules/${id}`);
  },

  pauseSchedule: async (id: string): Promise<Schedule> => {
    const response = await api.post<Schedule>(`/schedules/${id}/pause`);
    return response.data;
  },

  resumeSchedule: async (id: string): Promise<Schedule> => {
    const response = await api.post<Schedule>(`/schedules/${id}/resume`);
    return response.data;
  },
};
