import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import type { ZoneForecast } from "../api";

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

      <div style={{ display: "flex", gap: "0.5rem", margin: "1rem 0" }}>
        {forecast.has_active_advisory && (
          <span className="badge badge-danger">⚠ Active Advisory</span>
        )}
        {forecast.has_upcoming_advisory && (
          <span className="badge badge-warning">🔜 Upcoming Advisory</span>
        )}
        {!forecast.has_active_advisory && !forecast.has_upcoming_advisory && (
          <span className="badge badge-ok">✓ No Advisories</span>
        )}
      </div>

      {forecast.advisory_text && (
        <div
          className="card"
          style={{ borderColor: "var(--warning)", marginBottom: "1rem" }}
        >
          <div className="card-title" style={{ color: "var(--warning)", marginBottom: "0.5rem" }}>
            Advisory
          </div>
          <div style={{ fontSize: "0.9rem" }}>{forecast.advisory_text}</div>
        </div>
      )}

      <div className="card" style={{ marginBottom: "1rem" }}>
        <div className="card-title" style={{ marginBottom: "0.75rem" }}>
          Forecast
        </div>
        <div className="forecast-text" style={{ maxHeight: "none" }}>
          {forecast.forecast_text}
        </div>
      </div>

      <div className="status-bar" style={{ fontSize: "0.8rem" }}>
        {forecast.issued && (
          <span>
            Issued: {new Date(forecast.issued).toLocaleString()}
          </span>
        )}
        {forecast.expires && (
          <span>
            Expires: {new Date(forecast.expires).toLocaleString()}
          </span>
        )}
        <span>
          Fetched: {new Date(forecast.fetched_at).toLocaleString()}
        </span>
      </div>
    </>
  );
}
