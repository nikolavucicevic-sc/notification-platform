import { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import './Login.css';

function EyeIcon({ visible }: { visible: boolean }) {
  if (visible) {
    return (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
        <line x1="1" y1="1" x2="23" y2="23"/>
      </svg>
    );
  }
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
    </svg>
  );
}

export function Login() {
  const [isRegister, setIsRegister] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isRegister) {
        await axios.post('/api/auth/register', {
          username,
          email,
          password,
          full_name: fullName || null,
        });
        toast.success('Account created! Please sign in.');
        setIsRegister(false);
        setPassword('');
      } else {
        await login(username, password);
      }
    } catch (error: any) {
      if (isRegister) {
        toast.error(error.response?.data?.detail || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-left">
        <div className="login-brand">
          <div className="login-brand-icon">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 17H2a3 3 0 0 0 3-3V9a7 7 0 0 1 14 0v5a3 3 0 0 0 3 3zm-8.27 4a2 2 0 0 1-3.46 0"/>
            </svg>
          </div>
          <div>
            <h1>Bemby Notify</h1>
          </div>
        </div>
        <div className="login-tagline">
          <h2>Reach your customers,<br />wherever they are</h2>
          <p>Send targeted email and SMS notifications with scheduling, templates, and real-time delivery tracking.</p>
        </div>
        <div className="login-features">
          <div className="login-feature">
            <div className="feature-dot" />
            <span>Multi-channel delivery — Email &amp; SMS</span>
          </div>
          <div className="login-feature">
            <div className="feature-dot" />
            <span>Scheduled &amp; recurring notifications</span>
          </div>
          <div className="login-feature">
            <div className="feature-dot" />
            <span>Role-based access control</span>
          </div>
          <div className="login-feature">
            <div className="feature-dot" />
            <span>Real-time delivery monitoring</span>
          </div>
        </div>
      </div>

      <div className="login-right">
        <div className="login-card">
          <div className="login-header">
            <h3>{isRegister ? 'Create account' : 'Sign in'}</h3>
            <p>{isRegister ? 'Start sending notifications today' : 'Welcome back'}</p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {isRegister && (
              <>
                <div className="form-group">
                  <label htmlFor="email">Email address</label>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@company.com"
                    required
                    autoFocus
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="fullName">Full name <span className="optional">(optional)</span></label>
                  <input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="John Smith"
                  />
                </div>
              </>
            )}

            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                required
                autoFocus={!isRegister}
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <div className="password-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  className="password-toggle"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  <EyeIcon visible={showPassword} />
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="login-button"
              disabled={loading}
            >
              {loading
                ? (isRegister ? 'Creating account...' : 'Signing in...')
                : (isRegister ? 'Create account' : 'Sign in')
              }
            </button>
          </form>

          <div className="login-footer">
            <button
              type="button"
              className="toggle-mode-button"
              onClick={() => {
                setIsRegister(!isRegister);
                setPassword('');
                setEmail('');
                setFullName('');
              }}
            >
              {isRegister
                ? 'Already have an account? Sign in'
                : "Don't have an account? Create one"
              }
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
