import axios from 'axios';
import { Notification, NotificationCreate } from '../types/notification';
import { Customer, CustomerCreate } from '../types/customer';
import { Schedule, ScheduleCreate } from '../types/schedule';
import { Template, TemplateCreate, TemplateUpdate, TemplateRenderRequest, TemplateRenderResponse } from '../types/template';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;

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

// Template API
export const templateApi = {
  getTemplates: async (channel_type?: string): Promise<Template[]> => {
    const params = channel_type ? { channel_type } : {};
    const response = await api.get<Template[]>('/templates/', { params });
    return response.data;
  },

  getTemplate: async (id: string): Promise<Template> => {
    const response = await api.get<Template>(`/templates/${id}`);
    return response.data;
  },

  createTemplate: async (template: TemplateCreate): Promise<Template> => {
    const response = await api.post<Template>('/templates/', template);
    return response.data;
  },

  updateTemplate: async (id: string, template: TemplateUpdate): Promise<Template> => {
    const response = await api.put<Template>(`/templates/${id}`, template);
    return response.data;
  },

  deleteTemplate: async (id: string): Promise<void> => {
    await api.delete(`/templates/${id}`);
  },

  renderTemplate: async (request: TemplateRenderRequest): Promise<TemplateRenderResponse> => {
    const response = await api.post<TemplateRenderResponse>('/templates/render', request);
    return response.data;
  },
};
