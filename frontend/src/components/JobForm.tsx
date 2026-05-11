import { FormEvent, useEffect, useState } from 'react';
import type { Job, JobInput, JobStatus } from '../types/Job';

interface JobFormProps {
  editingJob: Job | null;
  onSubmit: (job: JobInput) => Promise<void>;
  onCancelEdit: () => void;
}

const emptyForm: JobInput = {
  company: '',
  job_title: '',
  job_url: '',
  date_applied: new Date().toISOString().slice(0, 10),
  status: 'Applied',
  salary_min: null,
  salary_max: null,
};

export function JobForm({ editingJob, onSubmit, onCancelEdit }: JobFormProps) {
  const [form, setForm] = useState<JobInput>(emptyForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formError, setFormError] = useState('');

  useEffect(() => {
    if (editingJob) {
      setForm({
        company: editingJob.company,
        job_title: editingJob.job_title,
        job_url: editingJob.job_url,
        date_applied: editingJob.date_applied.slice(0, 10),
        status: editingJob.status,
        salary_min: editingJob.salary_min ?? null,
        salary_max: editingJob.salary_max ?? null,
      });
    } else {
      setForm(emptyForm);
    }
  }, [editingJob]);

  function updateField(field: keyof JobInput, value: string) {
    setForm((current) => ({
      ...current,
      [field]: field.includes('salary') ? (value === '' ? null : Number(value)) : value,
    }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setFormError('');
    const salaryMin = form.salary_min ?? null;
    const salaryMax = form.salary_max ?? null;
    if (salaryMin !== null && salaryMax !== null && salaryMin > salaryMax) {
      setFormError('Salary minimum cannot be greater than salary maximum.');
      return;
    }
    setIsSubmitting(true);
    try {
      await onSubmit({
        ...form,
        date_applied: new Date(form.date_applied).toISOString(),
      });
      setForm(emptyForm);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="job-form" onSubmit={handleSubmit}>
      <div className="form-header">
        <h2>{editingJob ? 'Edit Application' : 'Add Application'}</h2>
        {editingJob && (
          <button className="ghost-button" type="button" onClick={onCancelEdit}>
            Cancel
          </button>
        )}
      </div>
      <div className="form-grid">
        <label>
          Company
          <input value={form.company} onChange={(event) => updateField('company', event.target.value)} required />
        </label>
        <label>
          Title
          <input value={form.job_title} onChange={(event) => updateField('job_title', event.target.value)} required />
        </label>
        <label className="wide">
          Job URL
          <input type="url" value={form.job_url} onChange={(event) => updateField('job_url', event.target.value)} required />
        </label>
        <label>
          Date Applied
          <input
            type="date"
            value={form.date_applied}
            onChange={(event) => updateField('date_applied', event.target.value)}
            required
          />
        </label>
        <label>
          Status
          <select value={form.status} onChange={(event) => updateField('status', event.target.value as JobStatus)}>
            <option value="Applied">Applied</option>
            <option value="Interview">Interview</option>
            <option value="Rejected">Rejected</option>
            <option value="Offer">Offer</option>
          </select>
        </label>
        <label>
          Salary Min
          <input
            type="number"
            min="0"
            value={form.salary_min ?? ''}
            onChange={(event) => updateField('salary_min', event.target.value)}
          />
        </label>
        <label>
          Salary Max
          <input
            type="number"
            min="0"
            value={form.salary_max ?? ''}
            onChange={(event) => updateField('salary_max', event.target.value)}
          />
        </label>
      </div>
      {formError && <p className="form-error">{formError}</p>}
      <button className="primary-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : editingJob ? 'Update Job' : 'Add Job'}
      </button>
    </form>
  );
}
