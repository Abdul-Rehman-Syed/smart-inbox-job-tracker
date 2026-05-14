import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';
import api from './services/api';

jest.mock('./services/api');

const mockedApi = api as jest.Mocked<typeof api>;

const baseStats = {
  total_applications: 1,
  interviews: 0,
  rejections: 0,
  pending: 1,
  by_status: { Applied: 1, Interview: 0, Rejected: 0, Offer: 0 },
  by_company: { Acme: 1 },
};

const baseJob = {
  id: 'job-1',
  company: 'Acme',
  job_title: 'Frontend Engineer',
  job_url: 'https://example.com/job',
  date_applied: '2026-05-11T00:00:00Z',
  status: 'Applied' as const,
  salary_min: 90000,
  salary_max: 120000,
  created_at: '2026-05-11T00:00:00Z',
  updated_at: '2026-05-11T00:00:00Z',
};

const baseUser = {
  id: 'user-1',
  email: 'test@example.com',
  full_name: 'Test User',
  created_at: '2026-05-11T00:00:00Z',
};

const baseEmailStatus = {
  provider: 'gmail',
  connected: false,
  connection: null,
};

beforeEach(() => {
  mockedApi.getToken.mockReturnValue('token');
  mockedApi.getMe.mockResolvedValue(baseUser);
  mockedApi.setToken.mockReturnValue(undefined);
  mockedApi.clearToken.mockReturnValue(undefined);
  mockedApi.getJobs.mockResolvedValue([baseJob]);
  mockedApi.getStats.mockResolvedValue(baseStats);
  mockedApi.getEmailStatus.mockResolvedValue(baseEmailStatus);
  mockedApi.getGmailConnectUrl.mockResolvedValue({ authorization_url: 'https://accounts.google.com/o/oauth2/v2/auth' });
  mockedApi.getEmailEvents.mockResolvedValue([]);
  mockedApi.syncEmail.mockResolvedValue({ scanned: 0, created_jobs: 0, updated_jobs: 0, needs_review: 0, skipped: 0 });
  mockedApi.disconnectEmail.mockResolvedValue({ connected: false });
  mockedApi.uploadJob.mockResolvedValue(baseJob);
  mockedApi.updateJob.mockResolvedValue(baseJob);
  mockedApi.deleteJob.mockResolvedValue(undefined);
  mockedApi.login.mockResolvedValue({ access_token: 'token', token_type: 'bearer', user: baseUser });
  mockedApi.register.mockResolvedValue({ access_token: 'token', token_type: 'bearer', user: baseUser });
});

test('renders dashboard statistics', async () => {
  render(<App />);
  expect(await screen.findByText('Total Applications')).toBeInTheDocument();
  expect(screen.getByText('Application Command Center')).toBeInTheDocument();
});

test('renders job list rows', async () => {
  render(<App />);
  expect(await screen.findByText('Acme')).toBeInTheDocument();
  expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
});

test('renders inbox sync panel', async () => {
  render(<App />);
  expect(await screen.findByText('Gmail Sync')).toBeInTheDocument();
  expect(screen.getByText('Not connected')).toBeInTheDocument();
});

test('submits a new job', async () => {
  render(<App />);
  await screen.findByText('Acme');
  await userEvent.clear(screen.getByLabelText(/Company/i));
  await userEvent.type(screen.getByLabelText(/Company/i), 'Globex');
  await userEvent.type(screen.getByLabelText(/^Title$/i), 'Backend Engineer');
  await userEvent.type(screen.getByLabelText(/Job URL/i), 'https://example.com/backend');
  await userEvent.click(screen.getByRole('button', { name: /Add Job/i }));
  await waitFor(() => expect(mockedApi.uploadJob).toHaveBeenCalled());
});

test('filters by last 7 days', async () => {
  const user = userEvent.setup();
  render(<App />);
  await user.click(await screen.findByRole('button', { name: /Last 7 Days/i }));
  await waitFor(() => expect(mockedApi.getJobs).toHaveBeenLastCalledWith({ date_range: '7d', status: '' }));
});

test('shows error when API load fails', async () => {
  mockedApi.getJobs.mockRejectedValueOnce(new Error('offline'));
  render(<App />);
  expect(await screen.findByText(/Could not load job applications/i)).toBeInTheDocument();
});

test('renders auth screen when logged out', async () => {
  mockedApi.getToken.mockReturnValue(null);
  render(<App />);
  expect(await screen.findByText('Welcome back')).toBeInTheDocument();
});
