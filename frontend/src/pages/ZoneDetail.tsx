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
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M10 12L6 8l4-4" />
          </svg>
          Back to Dashboard
        </Link>
        <h2>{forecast.zone_name}</h2>
        <p>{forecast.zone_id}</p>
      </div>

      <AdvisoryBadges forecast={forecast} />

      {forecast.advisory_text && (
        <div className="card card-advisory section-gap">
          <div className="card-title">Advisory</div>
          <div className="advisory-body">{forecast.advisory_text}</div>
        </div>
      )}

      <div className="card section-gap">
        <div className="card-title">Forecast</div>
        <div className="forecast-text forecast-text-full">
          {forecast.forecast_text}
        </div>
      </div>

      <div className="status-bar">
        <span><span aria-hidden="true">📋</span> Issued: {fmtTime(forecast.issued)}</span>
        <span><span aria-hidden="true">⏳</span> Expires: {fmtTime(forecast.expires)}</span>
        <span><span aria-hidden="true">🔄</span> Fetched: {fmtTime(forecast.fetched_at)}</span>
      </div>
    </>
  );
}
