interface Props {
  zoneId: string;
  error: string;
}

export function FailedZoneCard({ zoneId, error }: Props) {
  return (
    <div className="card-link">
      <div className="card card-failed">
        <div className="card-header">
          <span className="card-title">{zoneId}</span>
          <span className="badge badge-danger" role="status" aria-label="Failed to load">
            <span aria-hidden="true">✕</span> Failed
          </span>
        </div>
        <div className="failed-message">{error}</div>
      </div>
    </div>
  );
}
