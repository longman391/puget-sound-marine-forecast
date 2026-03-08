import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { AllForecastsResponse, CacheStatus } from "../api";

function timeAgo(iso: string | null): string {
  if (!iso) return "—";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  return `${Math.floor(mins / 60)}h ${mins % 60}m ago`;
}

function absTime(iso: string | null): string {
  if (!iso) return "";
  return new Date(iso).toLocaleString("en-US", {
    timeZone: "America/Los_Angeles",
    timeZoneName: "short",
  });
}

export default function Dashboard() {
  const [data, setData] = useState<AllForecastsResponse | null>(null);
  const [status, setStatus] = useState<CacheStatus | null>(null);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const load = () => {
    Promise.all([api.forecasts(), api.status()])
      .then(([f, s]) => {
        setData(f);
        setStatus(s);
        setError("");
      })
      .catch((e) => setError(e.message));
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await api.refresh();
      load();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setRefreshing(false);
    }
  };

  if (error && !data) return <div className="error-msg">Error: {error}</div>;
  if (!data) return <div className="loading">Loading forecasts…</div>;

  return (
    <>
      <div className="page-header">
        <h2>Marine Forecast Dashboard</h2>
        <p>Puget Sound &amp; Washington Coastal Waters</p>
      </div>

      <div className="status-bar">
        <span aria-label="Zones available">
          <span aria-hidden="true">🟢</span> {data.successful}/{data.total_zones} zones
        </span>
        <span aria-label={`Last updated ${absTime(data.cache_last_updated)}`}>
          <span aria-hidden="true">🕐</span> Updated {timeAgo(data.cache_last_updated)}
        </span>
        {status && (
          <span aria-label={`${status.total_updates} total refreshes`}>
            <span aria-hidden="true">⏱</span> {status.total_updates} refreshes
          </span>
        )}
        <button onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? "Refreshing…" : "↻ Refresh"}
        </button>
      </div>

      <div className="zone-grid">
        {data.forecasts.map((f) => {
          const cardClass = f.has_active_advisory
            ? "card card-danger"
            : f.has_upcoming_advisory
            ? "card card-advisory"
            : "card";

          return (
            <Link to={`/zone/${f.zone_id}`} key={f.zone_id} className="card-link">
              <div className={cardClass}>
                <div className="card-header">
                  <span className="card-title">{f.zone_name}</span>
                  <span className="setting-value">{f.zone_id}</span>
                </div>
                <div className="badge-row">
                  {f.has_active_advisory && (
                    <span className="badge badge-danger" role="status" aria-label="Active weather advisory">
                      <span aria-hidden="true">⚠</span> Active Advisory
                    </span>
                  )}
                  {f.has_upcoming_advisory && (
                    <span className="badge badge-warning" role="status" aria-label="Upcoming weather advisory">
                      <span aria-hidden="true">🔜</span> Upcoming
                    </span>
                  )}
                  {!f.has_active_advisory && !f.has_upcoming_advisory && (
                    <span className="badge badge-ok" role="status" aria-label="No advisories">
                      <span aria-hidden="true">✓</span> Clear
                    </span>
                  )}
                </div>
                {f.advisory_text && (
                  <div className="setting-value" style={{ color: "var(--warning)", marginBottom: "0.75rem" }}>
                    {f.advisory_text}
                  </div>
                )}
                <div className="forecast-text forecast-preview">
                  {f.forecast_text}
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </>
  );
}
