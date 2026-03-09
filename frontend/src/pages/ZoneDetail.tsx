import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api";
import type { ZoneForecast } from "../api";
import { AdvisoryBadges } from "../components/AdvisoryBadges";
import { fmtTime } from "../utils/time";

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

      <AdvisoryBadges forecast={forecast} />

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
