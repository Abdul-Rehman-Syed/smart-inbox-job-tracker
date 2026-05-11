import type { DateRange, JobStatus } from '../types/Job';

interface FiltersProps {
  dateRange: DateRange;
  status: JobStatus | '';
  onDateRangeChange: (value: DateRange) => void;
  onStatusChange: (value: JobStatus | '') => void;
}

const ranges: Array<{ label: string; value: DateRange }> = [
  { label: 'All Time', value: 'all' },
  { label: 'Last 7 Days', value: '7d' },
  { label: 'Last 30 Days', value: '30d' },
];

export function Filters({ dateRange, status, onDateRangeChange, onStatusChange }: FiltersProps) {
  return (
    <section className="toolbar" aria-label="Application filters">
      <div className="segmented" role="group" aria-label="Date range">
        {ranges.map((range) => (
          <button
            key={range.value}
            className={dateRange === range.value ? 'active' : ''}
            type="button"
            onClick={() => onDateRangeChange(range.value)}
          >
            {range.label}
          </button>
        ))}
      </div>
      <label className="select-label">
        Status
        <select value={status} onChange={(event) => onStatusChange(event.target.value as JobStatus | '')}>
          <option value="">All Statuses</option>
          <option value="Applied">Applied</option>
          <option value="Interview">Interview</option>
          <option value="Rejected">Rejected</option>
          <option value="Offer">Offer</option>
        </select>
      </label>
    </section>
  );
}
