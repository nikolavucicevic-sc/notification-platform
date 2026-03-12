import { useState } from 'react';
import NotificationForm from './components/NotificationForm';
import NotificationList from './components/NotificationList';
import './App.css';

function App() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleNotificationSuccess = () => {
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Notification Platform</h1>
        <p>Send email notifications to your customers</p>
      </header>

      <div className="app-content">
        <div className="form-section">
          <NotificationForm onSuccess={handleNotificationSuccess} />
        </div>

        <div className="list-section">
          <NotificationList refreshTrigger={refreshTrigger} />
        </div>
      </div>
    </div>
  );
}

export default App;
