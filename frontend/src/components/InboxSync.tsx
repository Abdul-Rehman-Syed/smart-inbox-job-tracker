import type { EmailConnectionStatus, EmailEvent, EmailSyncSummary } from '../types/Email';

interface InboxSyncProps {
  status: EmailConnectionStatus | null;
  events: EmailEvent[];
  summary: EmailSyncSummary | null;
  isLoading: boolean;
  onConnect: () => Promise<void>;
  onSync: () => Promise<void>;
  onDisconnect: () => Promise<void>;
}

function formatDate(value?: string | null) {
  if (!value) return 'Never';
  return new Date(value).toLocaleString();
}

export function InboxSync({ status, events, summary, isLoading, onConnect, onSync, onDisconnect }: InboxSyncProps) {
  const isConnected = Boolean(status?.connected);
  const recentEvents = events.slice(0, 4);

  return (
    <section className="inbox-panel" aria-label="Inbox sync">
      <div className="inbox-header">
        <div>
          <p className="eyebrow">Inbox Automation</p>
          <h2>Gmail Sync</h2>
        </div>
        <span className={isConnected ? 'connection-badge connected' : 'connection-badge'}>{isConnected ? 'Connected' : 'Not connected'}</span>
      </div>

      <p className="inbox-copy">
        Gmail automation will read job-related messages only after you connect a mailbox. The first version keeps syncing manual.
      </p>

      <dl className="inbox-meta">
        <div>
          <dt>Mailbox</dt>
          <dd>{status?.connection?.provider_email ?? 'No Gmail account connected'}</dd>
        </div>
        <div>
          <dt>Last sync</dt>
          <dd>{formatDate(status?.connection?.last_sync_at)}</dd>
        </div>
      </dl>

      {summary && (
        <div className="sync-summary">
          <span>{summary.scanned} scanned</span>
          <span>{summary.created_jobs} created</span>
          <span>{summary.updated_jobs} updated</span>
          <span>{summary.needs_review} review</span>
          <span>{summary.skipped} skipped</span>
        </div>
      )}

      <div className="inbox-actions">
        <button type="button" onClick={onConnect} disabled={isConnected || isLoading}>
          Connect Gmail
        </button>
        <button type="button" onClick={onSync} disabled={!isConnected || isLoading}>
          {isLoading ? 'Syncing...' : 'Sync Gmail'}
        </button>
        {isConnected && (
          <button className="danger-button" type="button" onClick={onDisconnect} disabled={isLoading}>
            Disconnect
          </button>
        )}
      </div>

      <div className="email-events">
        <h3>Recent detections</h3>
        {recentEvents.length > 0 ? (
          <ul>
            {recentEvents.map((event) => (
              <li key={event.id}>
                <strong>{event.detected_status ?? 'Unknown'}</strong>
                <span>{event.subject ?? 'No subject'}</span>
                <small>{event.sender ?? 'Unknown sender'}</small>
              </li>
            ))}
          </ul>
        ) : (
          <p>No email events yet.</p>
        )}
      </div>
    </section>
  );
}
