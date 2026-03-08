import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import type { ZoneForecast } from "../api";

function fmtTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("en-US", {
    timeZone: "America/Los_Angeles",
    timeZoneName: "short",
  });
}

export default function ZoneDetail() {
  const { zoneId } = useParams<{ zoneId: string }>();
  const [forecast, setForecast] = useState<ZoneForecast | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!zoneId) return;
    api
      .forecast(zoneId)
      .then((f) => {
        setForecast(f);
        setError("");
      })
      .catch((e) => setError(e.message));
  }, [zoneId]);

  if (error) return <div className="error-msg">Error: {error}</div>;
  if (!forecast) return <div className="loading">Loading forecast…</div>;

  return (
    <>
      <div className="page-header">
        <Link to="/" className="detail-back">
          ← Back to Dashboard
        </Link>
        <h2>{forecast.zone_name}</h2>
        <p>{forecast.zone_id}</p>
      </div>

      <div className="badge-row">
        {forecast.has_active_advisory && (
          <span className="badge badge-danger" role="status" aria-label="Active weather advisory">
            <span aria-hidden="true">⚠</span> Active Advisory
          </span>
        )}
        {forecast.has_upcoming_advisory && (
          <span className="badge badge-warning" role="status" aria-label="Upcoming weather advisory">
            <span aria-hidden="true">🔜</span> Upcoming Advisory
          </span>
        )}
        {!forecast.has_active_advisory && !forecast.has_upcoming_advisory && (
          <span className="badge badge-ok" role="status" aria-label="No advisories">
            <span aria-hidden="true">✓</span> No Advisories
          </span>
        )}
      </div>

      {forecast.advisory_text && (
        <div className="card card-danger section-gap">
          <div className="card-title" style={{ color: "var(--warning)", marginBottom: "0.5rem" }}>
            Advisory
          </div>
          <div style={{ fontSize: "0.9rem" }}>{forecast.advisory_text}</div>
        </div>
      )}

      <div className="card section-gap">
        <div className="card-title" style={{ marginBottom: "0.75rem" }}>
          Forecast
        </div>
        <div className="forecast-text" style={{ maxHeight: "none" }}>
          {forecast.forecast_text}
        </div>
      </div>

      <div className="status-bar">
        <span>Issued: {fmtTime(forecast.issued)}</span>
        <span>Expires: {fmtTime(forecast.expires)}</span>
        <span>Fetched: {fmtTime(forecast.fetched_at)}</span>
      </div>
    </>
  );
}
