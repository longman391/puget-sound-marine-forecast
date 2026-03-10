export function SkeletonCards({ count = 6 }: { count?: number }) {
  return (
    <div className="zone-grid">
      {Array.from({ length: count }).map((_, i) => (
        <div className="card-link" key={i}>
          <div className="card skeleton-card">
            <div className="skeleton-line skeleton-title" />
            <div className="skeleton-line skeleton-badge" />
            <div className="skeleton-block" />
          </div>
        </div>
      ))}
    </div>
  );
}
