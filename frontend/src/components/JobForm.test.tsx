import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { JobForm } from './JobForm';

test('renders add form fields', () => {
  render(<JobForm editingJob={null} onSubmit={jest.fn()} onCancelEdit={jest.fn()} />);
  expect(screen.getByLabelText(/Company/i)).toBeInTheDocument();
  expect(screen.getByLabelText(/Job URL/i)).toBeInTheDocument();
});

test('calls submit with form values', async () => {
  const user = userEvent.setup();
  const onSubmit = jest.fn().mockResolvedValue(undefined);
  render(<JobForm editingJob={null} onSubmit={onSubmit} onCancelEdit={jest.fn()} />);
  await user.type(screen.getByLabelText(/Company/i), 'Initech');
  await user.type(screen.getByLabelText(/^Title$/i), 'Product Engineer');
  await user.type(screen.getByLabelText(/Job URL/i), 'https://example.com/product');
  await user.click(screen.getByRole('button', { name: /Add Job/i }));
  expect(onSubmit).toHaveBeenCalledWith(expect.objectContaining({ company: 'Initech' }));
});

test('preloads editing job values', () => {
  render(
    <JobForm
      editingJob={{
        id: '1',
        company: 'Umbrella',
        job_title: 'Security Engineer',
        job_url: 'https://example.com/security',
        date_applied: '2026-05-11T00:00:00Z',
        status: 'Interview',
        salary_min: null,
        salary_max: null,
        created_at: '',
        updated_at: '',
      }}
      onSubmit={jest.fn()}
      onCancelEdit={jest.fn()}
    />,
  );
  expect(screen.getByDisplayValue('Umbrella')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /Update Job/i })).toBeInTheDocument();
});
