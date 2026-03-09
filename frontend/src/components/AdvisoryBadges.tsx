import type { ZoneForecast } from "../api";

export function AdvisoryBadges({ forecast }: { forecast: Pick<ZoneForecast, "has_active_advisory" | "has_upcoming_advisory"> }) {
  return (
    <div className="badge-row">
      {forecast.has_active_advisory && (
        <span className="badge badge-danger" role="status" aria-label="Active weather advisory">
          <span aria-hidden="true">⚠</span> Active Advisory
        </span>
      )}
      {forecast.has_upcoming_advisory && (
        <span className="badge badge-warning" role="status" aria-label="Upcoming weather advisory">
          <span aria-hidden="true">🔜</span> Upcoming
        </span>
      )}
      {!forecast.has_active_advisory && !forecast.has_upcoming_advisory && (
        <span className="badge badge-ok" role="status" aria-label="No advisories">
          <span aria-hidden="true">✓</span> Clear
        </span>
      )}
    </div>
  );
}
