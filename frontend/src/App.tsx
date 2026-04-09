import { useState } from 'react';
import NotificationForm from './components/NotificationForm';
import NotificationList from './components/NotificationList';
import { CustomerDashboard } from './components/CustomerDashboard';
import { SchedulerUI } from './components/SchedulerUI';
import { TemplateManager } from './components/TemplateManager';
import { MonitoringDashboard } from './components/MonitoringDashboard';
import { Login } from './components/Login';
import { AdminDashboard } from './components/AdminDashboard';
import { TenantsDashboard } from './components/TenantsDashboard';
import { UsageWidget } from './components/UsageWidget';
import { ProfileModal } from './components/ProfileModal';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';
import './App.css';

type Tab = 'notifications' | 'customers' | 'scheduler' | 'templates' | 'monitoring' | 'admin' | 'tenants';

const tabs: { id: Tab; label: string; icon: React.ReactNode; adminOnly?: boolean; superAdminOnly?: boolean }[] = [
  {
    id: 'notifications',
    label: 'Notifications',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"/>
      </svg>
    ),
  },
  {
    id: 'customers',
    label: 'Customers',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
      </svg>
    ),
  },
  {
    id: 'scheduler',
    label: 'Scheduler',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
    ),
  },
  {
    id: 'templates',
    label: 'Templates',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/>
        <polyline points="10 9 9 9 8 9"/>
      </svg>
    ),
  },
  {
    id: 'monitoring',
    label: 'Monitoring',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
      </svg>
    ),
  },
  {
    id: 'admin',
    label: 'Admin',
    adminOnly: true,
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M16.24 7.76a6 6 0 0 1 0 8.49M4.93 19.07a10 10 0 0 1 0-14.14M7.76 16.24a6 6 0 0 1 0-8.49"/>
      </svg>
    ),
  },
  {
    id: 'tenants',
    label: 'Tenants',
    superAdminOnly: true,
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
    ),
  },
];

function SunIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  );
}

function LogOutIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  );
}

function AppContent() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState<Tab>('notifications');
  const [showProfile, setShowProfile] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated, isAdmin, isSuperAdmin, logout, loading, refreshUsage } = useAuth();

  const handleNotificationSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
    refreshUsage();
  };

  if (loading) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="loading-spinner" />
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Login />;
  }

  const visibleTabs = tabs.filter(tab => {
    if (tab.superAdminOnly) return isSuperAdmin;
    if (tab.adminOnly) return isAdmin;
    return true;
  });

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <button className="header-brand" onClick={() => setActiveTab('notifications')}>
            <div className="brand-icon">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"/>
              </svg>
            </div>
            <div>
              <h1>Bemby Notify</h1>
            </div>
          </button>
          <div className="header-right">
            <button className="user-info" onClick={() => setShowProfile(true)} title="Edit profile">
              <div className="user-avatar">{user?.username?.[0]?.toUpperCase()}</div>
              <span className="user-name">{user?.full_name || user?.username}</span>
              <span className={`user-role role-${user?.role.toLowerCase()}`}>{user?.role}</span>
            </button>
            <button onClick={toggleTheme} className="icon-button" title="Toggle theme">
              {theme === 'light' ? <MoonIcon /> : <SunIcon />}
            </button>
            <button onClick={logout} className="logout-button">
              <LogOutIcon />
              <span>Sign out</span>
            </button>
          </div>
        </div>
      </header>

      <nav className="tab-navigation">
        <div className="tab-nav-inner">
          {visibleTabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {showProfile && <ProfileModal onClose={() => setShowProfile(false)} />}

      <div className="app-content">
        {activeTab === 'notifications' && (
          <div className="notifications-view">
            <div className="form-section">
              <UsageWidget />
              <NotificationForm onSuccess={handleNotificationSuccess} />
            </div>
            <div className="list-section">
              <NotificationList refreshTrigger={refreshTrigger} />
            </div>
          </div>
        )}
        {activeTab === 'customers' && <div className="single-panel-view"><CustomerDashboard /></div>}
        {activeTab === 'scheduler' && <div className="single-panel-view"><SchedulerUI /></div>}
        {activeTab === 'templates' && <div className="single-panel-view"><TemplateManager /></div>}
        {activeTab === 'monitoring' && <div className="single-panel-view"><MonitoringDashboard /></div>}
        {activeTab === 'admin' && isAdmin && <div className="single-panel-view"><AdminDashboard /></div>}
        {activeTab === 'tenants' && isSuperAdmin && <div className="single-panel-view"><TenantsDashboard /></div>}
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: 'var(--card-bg)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border)',
              borderRadius: '8px',
              fontSize: '0.875rem',
              boxShadow: 'var(--shadow-lg)',
            },
            success: {
              iconTheme: { primary: 'var(--success)', secondary: '#fff' },
            },
            error: {
              iconTheme: { primary: 'var(--danger)', secondary: '#fff' },
            },
          }}
        />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
