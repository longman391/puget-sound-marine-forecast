import { useEffect, useState } from "react";
import { api } from "../api";
import type { CacheStatus, ServerSettings } from "../api";
import { fmtTime } from "../utils/time";

function formatInterval(mins: number): string {
  if (mins < 60) return `${mins} minutes`;
  const h = mins / 60;
  return h === 1 ? "1 hour" : `${h} hours`;
}

const STATUS_DESCRIPTIONS: Record<string, string> = {
  health: "Overall system health status",
  zones_cached: "Forecast zones with current forecast data",
  last_updated: "Time of the most recent successful cache refresh",
  next_update: "Scheduled time for the next automatic refresh",
  total_refreshes: "Number of cache refresh cycles since server start",
  last_duration: "Time taken to complete the most recent refresh",
};

const CONFIG_DESCRIPTIONS: Record<string, string> = {
  cache_interval_minutes: "How often forecasts are refreshed from NOAA",
  auth_enabled: "Whether API key authentication is required",
  mcp_enabled: "Model Context Protocol server for AI agent integration",
  log_level: "Minimum severity level for server log output",
  noaa_base_url: "Source URL for marine forecast data files",
  allowed_origins: "Allowed origins for cross-origin API requests",
};

function SettingLabel({
  label,
  description,
  id,
}: {
  label: string;
  description: string;
  id: string;
}) {
  return (
    <div className="setting-label-group">
      <span className="setting-label" id={`${id}-label`}>{label}</span>
      <span className="setting-description" id={`${id}-desc`}>{description}</span>
    </div>
  );
}

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

      {/* --- Cache Status --- */}
      <div className="card section-gap">
        <div className="card-section-title">Cache Status</div>
        <div className="settings-grid">
          <div className="setting-row">
            <SettingLabel label="Health" description={STATUS_DESCRIPTIONS.health} id="status-health" />
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
            <SettingLabel label="Zones Cached" description={STATUS_DESCRIPTIONS.zones_cached} id="status-zones" />
            <span className="setting-value">
              {status.zones_cached} ok / {status.zones_failed} failed
            </span>
          </div>
          <div className="setting-row">
            <SettingLabel label="Last Updated" description={STATUS_DESCRIPTIONS.last_updated} id="status-last" />
            <span className="setting-value">{fmtTime(status.last_updated)}</span>
          </div>
          <div className="setting-row">
            <SettingLabel label="Next Update" description={STATUS_DESCRIPTIONS.next_update} id="status-next" />
            <span className="setting-value">{fmtTime(status.next_update)}</span>
          </div>
          <div className="setting-row">
            <SettingLabel label="Total Refreshes" description={STATUS_DESCRIPTIONS.total_refreshes} id="status-total" />
            <span className="setting-value">{status.total_updates}</span>
          </div>
          <div className="setting-row">
            <SettingLabel label="Last Refresh Duration" description={STATUS_DESCRIPTIONS.last_duration} id="status-dur" />
            <span className="setting-value">
              {status.last_update_duration_seconds
                ? `${status.last_update_duration_seconds.toFixed(2)}s`
                : "—"}
            </span>
          </div>
        </div>
      </div>

      {/* --- Configuration (read-only) --- */}
      <div className="card section-gap">
        <div className="card-section-title">Configuration</div>
        <p className="setting-description" style={{ marginBottom: "0.75rem" }}>
          These settings are controlled by environment variables. Restart the server to apply changes.
        </p>
        <div className="settings-grid">
          <div className="setting-row">
            <SettingLabel label="Cache Interval" description={CONFIG_DESCRIPTIONS.cache_interval_minutes} id="cfg-interval" />
            <span className="setting-value">{formatInterval(settings.cache_interval_minutes)}</span>
          </div>
          <div className="setting-row">
            <SettingLabel label="Auth Enabled" description={CONFIG_DESCRIPTIONS.auth_enabled} id="cfg-auth" />
            <span className="setting-value">{settings.auth_enabled ? "Yes" : "No"}</span>
          </div>
          <div className="setting-row">
            <SettingLabel label="MCP Server" description={CONFIG_DESCRIPTIONS.mcp_enabled} id="cfg-mcp" />
            <span className="setting-value">{settings.mcp_enabled ? "Enabled" : "Disabled"}</span>
          </div>
          <div className="setting-row">
            <SettingLabel label="Log Level" description={CONFIG_DESCRIPTIONS.log_level} id="cfg-loglevel" />
            <span className="setting-value">{settings.log_level}</span>
          </div>
          <div className="setting-row setting-row-stacked">
            <SettingLabel label="NOAA Base URL" description={CONFIG_DESCRIPTIONS.noaa_base_url} id="cfg-noaa" />
            <span className="setting-value mono-label">{settings.noaa_base_url}</span>
          </div>
          <div className="setting-row">
            <SettingLabel label="CORS Origins" description={CONFIG_DESCRIPTIONS.allowed_origins} id="cfg-cors" />
            <span className="setting-value">{settings.allowed_origins.join(", ")}</span>
          </div>
        </div>
      </div>

      {/* --- API Key --- */}
      <div className="card section-gap page-bottom">
        <label htmlFor="api-key-input" className="card-title">
          API Key
        </label>
        <p className="setting-description" id="api-key-help">
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
