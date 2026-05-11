import { Bar, BarChart, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { Stats } from '../types/Job';

interface ChartsProps {
  stats: Stats | null;
}

const colors: Record<string, string> = {
  Applied: '#56b6c2',
  Interview: '#d6b04c',
  Rejected: '#e06c75',
  Offer: '#7ccf8a',
};

export function Charts({ stats }: ChartsProps) {
  const statusData = Object.entries(stats?.by_status ?? {}).map(([name, value]) => ({ name, value }));
  const companyData = Object.entries(stats?.by_company ?? {}).map(([company, count]) => ({ company, count }));

  return (
    <section className="charts" aria-label="Application charts">
      <article className="chart-panel">
        <h2>Applications by Status</h2>
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie data={statusData} dataKey="value" nameKey="name" outerRadius={90} label>
              {statusData.map((entry) => (
                <Cell key={entry.name} fill={colors[entry.name] ?? '#9ba3af'} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </article>
      <article className="chart-panel">
        <h2>Top Companies</h2>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={companyData}>
            <XAxis dataKey="company" tick={{ fill: '#cbd5e1' }} />
            <YAxis allowDecimals={false} tick={{ fill: '#cbd5e1' }} />
            <Tooltip cursor={{ fill: 'rgba(255,255,255,0.08)' }} />
            <Bar dataKey="count" fill="#8fb3ff" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </article>
    </section>
  );
}
