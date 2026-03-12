import axios from 'axios';
import { Notification, NotificationCreate } from '../types/notification';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
