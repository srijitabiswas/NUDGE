export default function BarList({ items, emptyText = "No data yet." }) {
  const max = Math.max(1, ...items.map((i) => i.value));
  if (items.every((i) => i.value === 0)) return <p className="muted">{emptyText}</p>;
  return (
    <ul className="an-bars">
      {items.map((i) => (
        <li key={i.label} className="an-bar">
          <span className="an-label">{i.label}</span>
          <span className="an-track" aria-hidden="true">
            <span className={`an-fill ${i.tone || ""}`} style={{ width: `${(i.value / max) * 100}%` }} />
          </span>
          <span className="an-value">{i.value}</span>
        </li>
      ))}
    </ul>
  );
}