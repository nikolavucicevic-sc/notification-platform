import { useState } from 'react';
import NotificationForm from './components/NotificationForm';
import NotificationList from './components/NotificationList';
import { CustomerDashboard } from './components/CustomerDashboard';
import { SchedulerUI } from './components/SchedulerUI';
import { TemplateManager } from './components/TemplateManager';
import { MonitoringDashboard } from './components/MonitoringDashboard';
import { Login } from './components/Login';
import { AdminDashboard } from './components/AdminDashboard';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';
import './App.css';

type Tab = 'notifications' | 'customers' | 'scheduler' | 'templates' | 'monitoring' | 'admin';

function AppContent() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState<Tab>('notifications');
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated, isAdmin, logout, loading } = useAuth();

  const handleNotificationSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="app">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!isAuthenticated) {
    return <Login />;
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <h1>📢 Notification Platform</h1>
            <p>Send and track notifications to your customers</p>
          </div>
          <div className="header-right">
            <div className="user-info">
              <span className="user-name">{user?.username}</span>
              <span className={`user-role role-${user?.role.toLowerCase()}`}>{user?.role}</span>
            </div>
            <button onClick={toggleTheme} className="theme-toggle" title="Toggle theme">
              {theme === 'light' ? '🌙' : '☀️'}
            </button>
            <button onClick={logout} className="logout-button" title="Logout">
              🚪 Logout
            </button>
          </div>
        </div>
      </header>

      <nav className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'notifications' ? 'active' : ''}`}
          onClick={() => setActiveTab('notifications')}
        >
          📨 Notifications
        </button>
        <button
          className={`tab-button ${activeTab === 'customers' ? 'active' : ''}`}
          onClick={() => setActiveTab('customers')}
        >
          👥 Customers
        </button>
        <button
          className={`tab-button ${activeTab === 'scheduler' ? 'active' : ''}`}
          onClick={() => setActiveTab('scheduler')}
        >
          📅 Scheduler
        </button>
        <button
          className={`tab-button ${activeTab === 'templates' ? 'active' : ''}`}
          onClick={() => setActiveTab('templates')}
        >
          📝 Templates
        </button>
        <button
          className={`tab-button ${activeTab === 'monitoring' ? 'active' : ''}`}
          onClick={() => setActiveTab('monitoring')}
        >
          🔧 Monitoring
        </button>
        {isAdmin && (
          <button
            className={`tab-button ${activeTab === 'admin' ? 'active' : ''}`}
            onClick={() => setActiveTab('admin')}
          >
            👑 Admin
          </button>
        )}
      </nav>

      <div className="app-content">
        {activeTab === 'notifications' && (
          <div className="notifications-view">
            <div className="form-section">
              <NotificationForm onSuccess={handleNotificationSuccess} />
            </div>
            <div className="list-section">
              <NotificationList refreshTrigger={refreshTrigger} />
            </div>
          </div>
        )}

        {activeTab === 'customers' && (
          <div className="single-panel-view">
            <CustomerDashboard />
          </div>
        )}

        {activeTab === 'scheduler' && (
          <div className="single-panel-view">
            <SchedulerUI />
          </div>
        )}

        {activeTab === 'templates' && (
          <div className="single-panel-view">
            <TemplateManager />
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="single-panel-view">
            <MonitoringDashboard />
          </div>
        )}

        {activeTab === 'admin' && isAdmin && (
          <div className="single-panel-view">
            <AdminDashboard />
          </div>
        )}
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
            },
            success: {
              iconTheme: {
                primary: 'var(--success)',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: 'var(--danger)',
                secondary: '#fff',
              },
            },
          }}
        />
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
