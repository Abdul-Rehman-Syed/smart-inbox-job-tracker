import { useCallback, useEffect, useState } from 'react';
import './App.css';
import { Charts } from './components/Charts';
import { Dashboard } from './components/Dashboard';
import { Filters } from './components/Filters';
import { JobForm } from './components/JobForm';
import { JobList } from './components/JobList';
import api from './services/api';
import type { DateRange, Job, JobInput, JobStatus, Stats } from './types/Job';

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [dateRange, setDateRange] = useState<DateRange>('all');
  const [status, setStatus] = useState<JobStatus | ''>('');
  const [editingJob, setEditingJob] = useState<Job | null>(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

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
    refresh();
  }, [refresh]);

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

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Portfolio Job Tracker</p>
          <h1>Application Command Center</h1>
        </div>
        <span className="health-dot" aria-label="Application ready" />
      </header>

      {error && <div className="alert">{error}</div>}
      {notice && <div className="notice">{notice}</div>}

      <Dashboard stats={stats} />
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
