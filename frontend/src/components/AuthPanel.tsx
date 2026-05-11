import { FormEvent, useState } from 'react';
import type { AuthResponse } from '../types/API';

interface AuthPanelProps {
  onLogin: (auth: AuthResponse) => void;
  login: (payload: { email: string; password: string }) => Promise<AuthResponse>;
  register: (payload: { email: string; password: string; full_name?: string }) => Promise<AuthResponse>;
}

export function AuthPanel({ onLogin, login, register }: AuthPanelProps) {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      const auth =
        mode === 'login'
          ? await login({ email, password })
          : await register({ email, password, full_name: fullName || undefined });
      onLogin(auth);
    } catch {
      setError(mode === 'login' ? 'Invalid email or password.' : 'Could not create that account.');
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleDemoLogin() {
    setError('');
    setIsSubmitting(true);
    try {
      const auth = await login({ email: 'demo@example.com', password: 'password123' });
      onLogin(auth);
    } catch {
      setError('Demo account is not available yet. Run the demo seed script first.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <p className="eyebrow">Smart Inbox Job Tracker</p>
        <h1>{mode === 'login' ? 'Welcome back' : 'Create your workspace'}</h1>
        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === 'register' && (
            <label>
              Name
              <input value={fullName} onChange={(event) => setFullName(event.target.value)} placeholder="Ada Lovelace" />
            </label>
          )}
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={8}
              required
            />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Working...' : mode === 'login' ? 'Log In' : 'Create Account'}
          </button>
        </form>
        {mode === 'login' && (
          <button className="demo-button" type="button" onClick={handleDemoLogin} disabled={isSubmitting}>
            Use demo account
          </button>
        )}
        <button
          className="link-button"
          type="button"
          onClick={() => {
            setError('');
            setMode(mode === 'login' ? 'register' : 'login');
          }}
        >
          {mode === 'login' ? 'Create a new account' : 'Use an existing account'}
        </button>
      </section>
    </main>
  );
}
