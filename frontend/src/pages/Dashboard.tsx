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
        <p>Puget Sound & Washington Coastal Waters</p>
      </div>

      <div className="status-bar">
        <span>
          🟢 {data.successful}/{data.total_zones} zones
        </span>
        <span>🕐 Updated {timeAgo(data.cache_last_updated)}</span>
        {status && <span>⏱ {status.total_updates} refreshes</span>}
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          style={{ padding: "0.25rem 0.75rem", fontSize: "0.8rem" }}
        >
          {refreshing ? "Refreshing…" : "↻ Refresh"}
        </button>
      </div>

      <div className="zone-grid">
        {data.forecasts.map((f) => (
          <Link
            to={`/zone/${f.zone_id}`}
            key={f.zone_id}
            style={{ textDecoration: "none", color: "inherit" }}
          >
            <div className="card">
              <div className="card-header">
                <span className="card-title">{f.zone_name}</span>
                <span style={{ color: "var(--text-muted)", fontSize: "0.8rem" }}>
                  {f.zone_id}
                </span>
              </div>
              <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem" }}>
                {f.has_active_advisory && (
                  <span className="badge badge-danger">⚠ Active Advisory</span>
                )}
                {f.has_upcoming_advisory && (
                  <span className="badge badge-warning">🔜 Upcoming</span>
                )}
                {!f.has_active_advisory && !f.has_upcoming_advisory && (
                  <span className="badge badge-ok">✓ Clear</span>
                )}
              </div>
              {f.advisory_text && (
                <div
                  style={{
                    fontSize: "0.8rem",
                    color: "var(--warning)",
                    marginBottom: "0.5rem",
                  }}
                >
                  {f.advisory_text}
                </div>
              )}
              <div
                className="forecast-text"
                style={{ maxHeight: "120px", fontSize: "0.78rem" }}
              >
                {f.forecast_text.slice(0, 300)}
                {f.forecast_text.length > 300 ? "…" : ""}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </>
  );
}
