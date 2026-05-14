export interface EmailConnection {
  id: string;
  provider: string;
  provider_email: string;
  scopes: string;
  last_sync_at?: string | null;
  created_at: string;
}

export interface EmailConnectionStatus {
  provider: string;
  connected: boolean;
  connection?: EmailConnection | null;
}

export interface GmailConnectUrl {
  authorization_url: string;
}

export interface EmailEvent {
  id: string;
  job_id?: string | null;
  provider: string;
  message_id: string;
  thread_id?: string | null;
  sender?: string | null;
  subject?: string | null;
  received_at?: string | null;
  detected_company?: string | null;
  detected_job_title?: string | null;
  detected_status?: string | null;
  processing_status: string;
  note?: string | null;
  created_at: string;
}

export interface EmailSyncSummary {
  scanned: number;
  created_jobs: number;
  updated_jobs: number;
  needs_review: number;
  skipped: number;
}
