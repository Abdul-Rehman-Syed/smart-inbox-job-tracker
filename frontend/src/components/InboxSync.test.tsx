import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InboxSync } from './InboxSync';

test('renders disconnected Gmail state', () => {
  render(
    <InboxSync
      status={{ provider: 'gmail', connected: false, connection: null }}
      events={[]}
      summary={null}
      isLoading={false}
      onSync={jest.fn()}
      onDisconnect={jest.fn()}
    />,
  );

  expect(screen.getByText('Gmail Sync')).toBeInTheDocument();
  expect(screen.getByText('Not connected')).toBeInTheDocument();
  expect(screen.getByText('No email events yet.')).toBeInTheDocument();
});

test('renders connected state and calls sync', async () => {
  const user = userEvent.setup();
  const onSync = jest.fn().mockResolvedValue(undefined);

  render(
    <InboxSync
      status={{
        provider: 'gmail',
        connected: true,
        connection: {
          id: 'connection-1',
          provider: 'gmail',
          provider_email: 'demo@gmail.com',
          scopes: 'gmail.readonly',
          last_sync_at: '2026-05-14T08:00:00Z',
          created_at: '2026-05-14T08:00:00Z',
        },
      }}
      events={[
        {
          id: 'event-1',
          provider: 'gmail',
          message_id: 'message-1',
          sender: 'jobs@example.com',
          subject: 'Interview invitation',
          detected_status: 'Interview',
          processing_status: 'Updated',
          created_at: '2026-05-14T08:00:00Z',
        },
      ]}
      summary={{ scanned: 3, created_jobs: 1, updated_jobs: 1, needs_review: 0, skipped: 1 }}
      isLoading={false}
      onSync={onSync}
      onDisconnect={jest.fn()}
    />,
  );

  expect(screen.getByText('Connected')).toBeInTheDocument();
  expect(screen.getByText('demo@gmail.com')).toBeInTheDocument();
  expect(screen.getByText('Interview invitation')).toBeInTheDocument();
  expect(screen.getByText('3 scanned')).toBeInTheDocument();

  await user.click(screen.getByRole('button', { name: /Sync Gmail/i }));

  expect(onSync).toHaveBeenCalledTimes(1);
});
