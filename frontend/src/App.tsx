import { useState } from 'react';
import NotificationForm from './components/NotificationForm';
import NotificationList from './components/NotificationList';
import { CustomerDashboard } from './components/CustomerDashboard';
import { SchedulerUI } from './components/SchedulerUI';
import { TemplateManager } from './components/TemplateManager';
import { MonitoringDashboard } from './components/MonitoringDashboard';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { Toaster } from 'react-hot-toast';
import './App.css';

type Tab = 'notifications' | 'customers' | 'scheduler' | 'templates' | 'monitoring';

function AppContent() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [activeTab, setActiveTab] = useState<Tab>('notifications');
  const { theme, toggleTheme } = useTheme();

  const handleNotificationSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <h1>📢 Notification Platform</h1>
            <p>Send and track notifications to your customers</p>
          </div>
          <button onClick={toggleTheme} className="theme-toggle" title="Toggle theme">
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
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
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
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
    </ThemeProvider>
  );
}

export default App;
