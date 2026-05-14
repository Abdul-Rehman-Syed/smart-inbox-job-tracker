export type JobStatus = 'Applied' | 'Interview' | 'Rejected' | 'Offer';
export type DateRange = 'all' | '7d' | '30d';

export interface Job {
  id: string;
  company: string;
  job_title: string;
  job_url: string;
  date_applied: string;
  status: JobStatus;
  salary_min?: number | null;
  salary_max?: number | null;
  created_at: string;
  updated_at: string;
  status_history?: JobStatusHistory[];
}

export interface JobStatusHistory {
  id: string;
  job_id: string;
  old_status?: JobStatus | null;
  new_status: JobStatus;
  source: string;
  note?: string | null;
  created_at: string;
}

export interface JobInput {
  company: string;
  job_title: string;
  job_url: string;
  date_applied: string;
  status: JobStatus;
  salary_min?: number | null;
  salary_max?: number | null;
}

export interface Stats {
  total_applications: number;
  interviews: number;
  rejections: number;
  pending: number;
  by_status: Record<string, number>;
  by_company: Record<string, number>;
}

export interface JobFilters {
  date_range?: DateRange;
  status?: JobStatus | '';
}
