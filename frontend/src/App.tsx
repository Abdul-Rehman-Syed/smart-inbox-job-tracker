import { useCallback, useEffect, useState } from 'react';
import './App.css';
import { AuthPanel } from './components/AuthPanel';
import { Charts } from './components/Charts';
import { Dashboard } from './components/Dashboard';
import { Filters } from './components/Filters';
import { InboxSync } from './components/InboxSync';
import { JobForm } from './components/JobForm';
import { JobList } from './components/JobList';
import api from './services/api';
import type { AuthResponse, User } from './types/API';
import type { EmailConnectionStatus, EmailEvent, EmailSyncSummary } from './types/Email';
import type { DateRange, Job, JobInput, JobStatus, Stats } from './types/Job';

function App() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthLoading, setIsAuthLoading] = useState(Boolean(api.getToken()));
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [emailStatus, setEmailStatus] = useState<EmailConnectionStatus | null>(null);
  const [emailEvents, setEmailEvents] = useState<EmailEvent[]>([]);
  const [emailSummary, setEmailSummary] = useState<EmailSyncSummary | null>(null);
  const [dateRange, setDateRange] = useState<DateRange>('all');
  const [status, setStatus] = useState<JobStatus | ''>('');
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isEmailLoading, setIsEmailLoading] = useState(false);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const [jobsResult, statsResult] = await Promise.all([
        api.getJobs({ date_range: dateRange, status }),
        api.getStats(dateRange),
      ]);
      setJobs(jobsResult);
      setStats(statsResult);
    } catch (err) {
      setError('Could not load job applications. Check the API connection and try again.');
    } finally {
      setIsLoading(false);
    }
  }, [dateRange, status]);

  const refreshEmail = useCallback(async () => {
    try {
      const [statusResult, eventsResult] = await Promise.all([api.getEmailStatus(), api.getEmailEvents()]);
      setEmailStatus(statusResult);
      setEmailEvents(eventsResult);
    } catch {
      setEmailStatus({ provider: 'gmail', connected: false, connection: null });
      setEmailEvents([]);
    }
  }, []);

  const visibleJobs = jobs.filter((job) => {
    const query = searchTerm.trim().toLowerCase();
    if (!query) return true;
    return `${job.company} ${job.job_title}`.toLowerCase().includes(query);
  });

  function showNotice(message: string) {
    setNotice(message);
    window.setTimeout(() => setNotice(''), 3500);
  }

  useEffect(() => {
    const token = api.getToken();
    if (!token) {
      setIsAuthLoading(false);
      return;
    }
    api
      .getMe()
      .then((user) => {
        setCurrentUser(user);
      })
      .catch(() => {
        api.clearToken();
      })
      .finally(() => setIsAuthLoading(false));
  }, []);

  useEffect(() => {
    if (currentUser) {
      refresh();
      refreshEmail();
    }
  }, [currentUser, refresh, refreshEmail]);

  function handleAuth(auth: AuthResponse) {
    api.setToken(auth.access_token);
    setCurrentUser(auth.user);
    showNotice(`Signed in as ${auth.user.email}.`);
  }

  function handleLogout() {
    api.clearToken();
    setCurrentUser(null);
    setJobs([]);
    setStats(null);
    setEmailStatus(null);
    setEmailEvents([]);
    setEmailSummary(null);
    setEditingJob(null);
    setNotice('');
    setError('');
  }

  async function handleSubmit(job: JobInput) {
    setError('');
    try {
      if (editingJob) {
        await api.updateJob(editingJob.id, job);
        setEditingJob(null);
        showNotice('Application updated.');
      } else {
        await api.uploadJob(job);
        showNotice('Application added.');
      }
      await refresh();
    } catch (err) {
      setError('Could not save the application. Check the form and try again.');
      throw err;
    }
  }

  async function handleDelete(id: string) {
    const job = jobs.find((item) => item.id === id);
    const label = job ? `${job.company} - ${job.job_title}` : 'this application';
    if (!window.confirm(`Delete ${label}?`)) return;
    setError('');
    try {
      await api.deleteJob(id);
      showNotice('Application deleted.');
      await refresh();
    } catch {
      setError('Could not delete the application. Try again.');
    }
  }

  async function handleStatusChange(id: string, nextStatus: JobStatus) {
    setError('');
    try {
      await api.updateJob(id, { status: nextStatus });
      showNotice(`Status changed to ${nextStatus}.`);
      await refresh();
    } catch {
      setError('Could not update the status. Try again.');
    }
  }

  async function handleEmailSync() {
    setIsEmailLoading(true);
    setError('');
    try {
      const summary = await api.syncEmail();
      setEmailSummary(summary);
      await Promise.all([refresh(), refreshEmail()]);
      showNotice('Gmail sync completed.');
    } catch {
      setError('Could not sync Gmail. Connect a mailbox before syncing.');
    } finally {
      setIsEmailLoading(false);
    }
  }

  async function handleEmailDisconnect() {
    setIsEmailLoading(true);
    setError('');
    try {
      await api.disconnectEmail();
      setEmailSummary(null);
      await refreshEmail();
      showNotice('Gmail disconnected.');
    } catch {
      setError('Could not disconnect Gmail. Try again.');
    } finally {
      setIsEmailLoading(false);
    }
  }

  if (isAuthLoading) {
    return <main className="app-shell">Loading account...</main>;
  }

  if (!currentUser) {
    return <AuthPanel onLogin={handleAuth} login={api.login} register={api.register} />;
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Portfolio Job Tracker</p>
          <h1>Application Command Center</h1>
          <p className="user-line">{currentUser.email}</p>
        </div>
        <button className="ghost-button" type="button" onClick={handleLogout}>
          Log Out
        </button>
      </header>

      {error && <div className="alert">{error}</div>}
      {notice && <div className="notice">{notice}</div>}

      <Dashboard stats={stats} />
      <InboxSync
        status={emailStatus}
        events={emailEvents}
        summary={emailSummary}
        isLoading={isEmailLoading}
        onSync={handleEmailSync}
        onDisconnect={handleEmailDisconnect}
      />
      <Filters dateRange={dateRange} status={status} onDateRangeChange={setDateRange} onStatusChange={setStatus} />

      <div className="content-grid">
        <JobForm editingJob={editingJob} onSubmit={handleSubmit} onCancelEdit={() => setEditingJob(null)} />
        <div className="list-column">
          <label className="search-box">
            Search applications
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Company or title"
            />
          </label>
          {isLoading ? <div className="loading">Loading applications...</div> : null}
          <JobList jobs={visibleJobs} onEdit={setEditingJob} onDelete={handleDelete} onStatusChange={handleStatusChange} />
        </div>
      </div>

      <Charts stats={stats} />
    </main>
  );
}

export default App;
