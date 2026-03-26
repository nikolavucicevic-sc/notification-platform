import { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import './Login.css';

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
        // Register new user
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
        // Login
        await login(username, password);
      }
    } catch (error: any) {
      // Error toast already shown by auth context for login
      // Show error for registration
      if (isRegister) {
        toast.error(error.response?.data?.detail || 'Registration failed');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🔐 Notification Platform</h1>
          <p>{isRegister ? 'Create your account' : 'Sign in to continue'}</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {isRegister && (
            <>
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  autoFocus
                />
              </div>

              <div className="form-group">
                <label htmlFor="fullName">Full Name (optional)</label>
                <input
                  id="fullName"
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Enter your full name"
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
                {showPassword ? '👁️' : '👁️‍🗨️'}
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
              : (isRegister ? 'Create Account' : 'Sign In')
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
          <p className="login-info">
            Enterprise-grade authentication with JWT & RBAC
          </p>
        </div>
      </div>
    </div>
  );
}
