import type { Stats } from '../types/Job';

interface DashboardProps {
  stats: Stats | null;
}

export function Dashboard({ stats }: DashboardProps) {
  const cards = [
    { label: 'Total Applications', value: stats?.total_applications ?? 0 },
    { label: 'Interviews', value: stats?.interviews ?? 0 },
    { label: 'Rejections', value: stats?.rejections ?? 0 },
    { label: 'Pending', value: stats?.pending ?? 0 },
  ];

  return (
    <section className="dashboard" aria-label="Dashboard statistics">
      {cards.map((card) => (
        <article className="stat-card" key={card.label}>
          <span>{card.label}</span>
          <strong>{card.value}</strong>
        </article>
      ))}
    </section>
  );
}
