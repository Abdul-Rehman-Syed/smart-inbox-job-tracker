import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuthPanel } from './AuthPanel';

const auth = {
  access_token: 'token',
  token_type: 'bearer' as const,
  user: {
    id: 'user-1',
    email: 'test@example.com',
    full_name: 'Test User',
    created_at: '2026-05-11T00:00:00Z',
  },
};

test('logs in with email and password', async () => {
  const user = userEvent.setup();
  const login = jest.fn().mockResolvedValue(auth);
  const onLogin = jest.fn();
  render(<AuthPanel onLogin={onLogin} login={login} register={jest.fn()} />);
  await user.type(screen.getByLabelText(/Email/i), 'test@example.com');
  await user.type(screen.getByLabelText(/Password/i), 'password123');
  await user.click(screen.getByRole('button', { name: /Log In/i }));
  expect(login).toHaveBeenCalledWith({ email: 'test@example.com', password: 'password123' });
  expect(onLogin).toHaveBeenCalledWith(auth);
});

test('switches to registration mode', async () => {
  const user = userEvent.setup();
  render(<AuthPanel onLogin={jest.fn()} login={jest.fn()} register={jest.fn()} />);
  await user.click(screen.getByRole('button', { name: /Create a new account/i }));
  expect(screen.getByText('Create your workspace')).toBeInTheDocument();
  expect(screen.getByLabelText(/Name/i)).toBeInTheDocument();
});
