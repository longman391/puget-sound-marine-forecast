import { useEffect, useState } from "react";
import { api } from "../api";
import type { CacheStatus, ServerSettings } from "../api";
import { fmtTime } from "../utils/time";

export default function Settings() {
  const [status, setStatus] = useState<CacheStatus | null>(null);
  const [settings, setSettings] = useState<ServerSettings | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.status(), api.settings()])
      .then(([s, cfg]) => {
        setStatus(s);
        setSettings(cfg);
      })
      .catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="error-msg">Error: {error}</div>;
  if (!status || !settings) return <div className="loading">Loading…</div>;

  return (
    <>
      <div className="page-header">
        <h2>Server Settings &amp; Status</h2>
        <p>Cache health, configuration, and API access</p>
      </div>

      <div className="card section-gap">
        <div className="card-section-title">Cache Status</div>
        <div className="settings-grid">
          <div className="setting-row">
            <span className="setting-label">Health</span>
            <span
              className={`badge ${
                status.health === "healthy"
                  ? "badge-ok"
                  : status.health === "degraded"
                  ? "badge-warning"
                  : "badge-danger"
              }`}
            >
              {status.health}
            </span>
          </div>
          <div className="setting-row">
            <span className="setting-label">Zones Cached</span>
            <span className="setting-value">
              {status.zones_cached} ok / {status.zones_failed} failed
            </span>
          </div>
          <div className="setting-row">
            <span className="setting-label">Last Updated</span>
            <span className="setting-value">{fmtTime(status.last_updated)}</span>
          </div>
          <div className="setting-row">
            <span className="setting-label">Next Update</span>
            <span className="setting-value">{fmtTime(status.next_update)}</span>
          </div>
          <div className="setting-row">
            <span className="setting-label">Total Refreshes</span>
            <span className="setting-value">{status.total_updates}</span>
          </div>
          <div className="setting-row">
            <span className="setting-label">Last Refresh Duration</span>
            <span className="setting-value">
              {status.last_update_duration_seconds
                ? `${status.last_update_duration_seconds.toFixed(2)}s`
                : "—"}
            </span>
          </div>
        </div>
      </div>

      <div className="card section-gap">
        <div className="card-section-title">Configuration</div>
        <div className="settings-grid">
          <div className="setting-row">
            <span className="setting-label">Cache Interval</span>
            <span className="setting-value">
              {settings.cache_interval_minutes} minutes
            </span>
          </div>
          <div className="setting-row">
            <span className="setting-label">Auth Enabled</span>
            <span className="setting-value">
              {settings.auth_enabled ? "Yes" : "No"}
            </span>
          </div>
          <div className="setting-row">
            <span className="setting-label">MCP Server</span>
            <span className="setting-value">
              {settings.mcp_enabled ? "Enabled" : "Disabled"}
            </span>
          </div>
          <div className="setting-row">
            <span className="setting-label">Log Level</span>
            <span className="setting-value">{settings.log_level}</span>
          </div>
          <div className="setting-row">
            <span className="setting-label">NOAA Base URL</span>
            <span className="setting-value">{settings.noaa_base_url}</span>
          </div>
          <div className="setting-row">
            <span className="setting-label">CORS Origins</span>
            <span className="setting-value">
              {settings.allowed_origins.join(", ")}
            </span>
          </div>
        </div>
      </div>

      <div className="card section-gap page-bottom">
        <label htmlFor="api-key-input" className="card-title">
          API Key
        </label>
        <p id="api-key-help" className="help-text">
          If the server has auth enabled, enter your API key here. It will be
          stored in your browser's localStorage.
        </p>
        <input
          id="api-key-input"
          className="input"
          type="password"
          placeholder="Enter API key…"
          aria-describedby="api-key-help"
          defaultValue={localStorage.getItem("api_key") || ""}
          onChange={(e) => {
            if (e.target.value) {
              localStorage.setItem("api_key", e.target.value);
            } else {
              localStorage.removeItem("api_key");
            }
          }}
        />
      </div>
    </>
  );
}
