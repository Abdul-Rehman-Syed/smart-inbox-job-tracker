import { Fragment, useState } from 'react';
import type { Job, JobStatus } from '../types/Job';

interface JobListProps {
  jobs: Job[];
  onEdit: (job: Job) => void;
  onDelete: (id: string) => Promise<void>;
  onStatusChange: (id: string, status: JobStatus) => Promise<void>;
}

function formatCurrency(min?: number | null, max?: number | null) {
  if (!min && !max) return 'Not listed';
  const formatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 });
  if (min && max) return `${formatter.format(min)} - ${formatter.format(max)}`;
  return formatter.format(min ?? max ?? 0);
}

export function JobList({ jobs, onEdit, onDelete, onStatusChange }: JobListProps) {
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);

  return (
    <section className="table-shell" aria-label="Job applications">
      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Title</th>
            <th>Date</th>
            <th>Status</th>
            <th>Salary</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => {
            const isExpanded = expandedJobId === job.id;
            const history = job.status_history ?? [];
            return (
              <Fragment key={job.id}>
                <tr>
                  <td>
                    <a href={job.job_url} target="_blank" rel="noreferrer">
                      {job.company}
                    </a>
                  </td>
                  <td>{job.job_title}</td>
                  <td>{new Date(job.date_applied).toLocaleDateString()}</td>
                  <td>
                    <select
                      className={`status-pill ${job.status.toLowerCase()}`}
                      value={job.status}
                      onChange={(event) => onStatusChange(job.id, event.target.value as JobStatus)}
                    >
                      <option value="Applied">Applied</option>
                      <option value="Interview">Interview</option>
                      <option value="Rejected">Rejected</option>
                      <option value="Offer">Offer</option>
                    </select>
                  </td>
                  <td>{formatCurrency(job.salary_min, job.salary_max)}</td>
                  <td>
                    <div className="row-actions">
                      <button type="button" onClick={() => onEdit(job)}>
                        Edit
                      </button>
                      <button type="button" onClick={() => setExpandedJobId(isExpanded ? null : job.id)}>
                        History
                      </button>
                      <button className="danger-button" type="button" onClick={() => onDelete(job.id)}>
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
                {isExpanded && (
                  <tr className="history-row">
                    <td colSpan={6}>
                      {history.length > 0 ? (
                        <ol className="status-history">
                          {history.map((item) => (
                            <li key={item.id}>
                              <strong>{item.new_status}</strong>
                              <span>
                                {item.old_status ? `${item.old_status} -> ${item.new_status}` : `Created as ${item.new_status}`}
                              </span>
                              <small>
                                {item.source} - {new Date(item.created_at).toLocaleString()}
                              </small>
                              {item.note && <em>{item.note}</em>}
                            </li>
                          ))}
                        </ol>
                      ) : (
                        <p className="history-empty">No status history recorded yet.</p>
                      )}
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
          {jobs.length === 0 && (
            <tr>
              <td className="empty-state" colSpan={6}>
                No applications match the current filters.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
