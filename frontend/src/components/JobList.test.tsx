import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { JobList } from './JobList';

const job = {
  id: '1',
  company: 'Acme',
  job_title: 'Frontend Engineer',
  job_url: 'https://example.com/job',
  date_applied: '2026-05-11T00:00:00Z',
  status: 'Applied' as const,
  salary_min: 100000,
  salary_max: 130000,
  created_at: '',
  updated_at: '',
  status_history: [
    {
      id: 'history-1',
      job_id: '1',
      old_status: null,
      new_status: 'Applied' as const,
      source: 'manual',
      note: 'Application created',
      created_at: '2026-05-11T00:00:00Z',
    },
  ],
};

test('renders empty state', () => {
  render(<JobList jobs={[]} onEdit={jest.fn()} onDelete={jest.fn()} onStatusChange={jest.fn()} />);
  expect(screen.getByText(/No applications match/i)).toBeInTheDocument();
});

test('renders job row', () => {
  render(<JobList jobs={[job]} onEdit={jest.fn()} onDelete={jest.fn()} onStatusChange={jest.fn()} />);
  expect(screen.getByText('Acme')).toBeInTheDocument();
  expect(screen.getByText(/100,000/)).toBeInTheDocument();
});

test('calls edit and delete handlers', async () => {
  const user = userEvent.setup();
  const onEdit = jest.fn();
  const onDelete = jest.fn().mockResolvedValue(undefined);
  render(<JobList jobs={[job]} onEdit={onEdit} onDelete={onDelete} onStatusChange={jest.fn()} />);
  await user.click(screen.getByRole('button', { name: /Edit/i }));
  await user.click(screen.getByRole('button', { name: /Delete/i }));
  expect(onEdit).toHaveBeenCalledWith(job);
  expect(onDelete).toHaveBeenCalledWith('1');
});

test('calls status handler', async () => {
  const user = userEvent.setup();
  const onStatusChange = jest.fn().mockResolvedValue(undefined);
  render(<JobList jobs={[job]} onEdit={jest.fn()} onDelete={jest.fn()} onStatusChange={onStatusChange} />);
  await user.selectOptions(screen.getByDisplayValue('Applied'), 'Interview');
  expect(onStatusChange).toHaveBeenCalledWith('1', 'Interview');
});

test('toggles status history', async () => {
  const user = userEvent.setup();
  render(<JobList jobs={[job]} onEdit={jest.fn()} onDelete={jest.fn()} onStatusChange={jest.fn()} />);
  await user.click(screen.getByRole('button', { name: /History/i }));
  expect(screen.getByText(/Created as Applied/i)).toBeInTheDocument();
  expect(screen.getByText(/Application created/i)).toBeInTheDocument();
});
