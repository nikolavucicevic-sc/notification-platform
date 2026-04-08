import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  role: 'ADMIN' | 'OPERATOR' | 'VIEWER';
  is_active: boolean;
  email_limit: number | null;
  sms_limit: number | null;
  email_sent: number;
  sms_sent: number;
}

export interface UsageStats {
  email_limit: number | null;
  sms_limit: number | null;
  email_sent: number;
  sms_sent: number;
  email_remaining: number | null;
  sms_remaining: number | null;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  usage: UsageStats | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUsage: () => Promise<void>;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isOperatorOrAdmin: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [usage, setUsage] = useState<UsageStats | null>(null);
  const [loading, setLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    if (savedToken) {
      setToken(savedToken);
      fetchCurrentUser(savedToken);
    } else {
      setLoading(false);
    }
  }, []);

  // Set up axios interceptor for auth token
  useEffect(() => {
    const interceptor = axios.interceptors.request.use((config) => {
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    return () => axios.interceptors.request.eject(interceptor);
  }, [token]);

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const response = await axios.get('/api/auth/me', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      setUser(response.data);
      await fetchUsage(authToken);
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchUsage = async (authToken?: string) => {
    try {
      const headers = authToken ? { Authorization: `Bearer ${authToken}` } : undefined;
      const response = await axios.get('/api/auth/users/me/usage', { headers });
      setUsage(response.data);
    } catch (error) {
      console.error('Failed to fetch usage stats:', error);
    }
  };

  const refreshUsage = async () => {
    await fetchUsage();
  };

  const refreshUser = async () => {
    await fetchCurrentUser(token!);
  };

  const login = async (username: string, password: string) => {
    try {
      const response = await axios.post('/api/auth/login', { username, password });
      const { access_token } = response.data;
      setToken(access_token);
      localStorage.setItem('auth_token', access_token);
      await fetchCurrentUser(access_token);
      toast.success('Login successful!');
    } catch (error: any) {
      console.error('Login failed:', error);
      toast.error(error.response?.data?.detail || 'Login failed');
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setUsage(null);
    localStorage.removeItem('auth_token');
    toast.success('Logged out successfully');
  };

  const value: AuthContextType = {
    user,
    token,
    usage,
    login,
    logout,
    refreshUsage,
    refreshUser,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'ADMIN',
    isOperatorOrAdmin: user?.role === 'ADMIN' || user?.role === 'OPERATOR',
    loading
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
