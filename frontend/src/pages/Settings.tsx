import { useEffect, useState } from "react";
import { api } from "../api";
import type { CacheStatus, ServerSettings } from "../api";
import { useLocalSettings } from "../hooks/useLocalSettings";
import type { LocalSettings, SaveStatus } from "../hooks/useLocalSettings";
import { fmtTime } from "../utils/time";

const CACHE_INTERVAL_OPTIONS = [30, 60, 90, 120, 150, 180, 210, 240];
const LOG_LEVEL_OPTIONS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"];

function formatInterval(mins: number): string {
  if (mins < 60) return `${mins} minutes`;
  const h = mins / 60;
  return h === 1 ? "1 hour" : `${h} hours`;
}

function validateUrl(value: string): string | null {
  if (!value.trim()) return "URL is required";
  if (!/^https?:\/\//.test(value)) return "Must start with http:// or https://";
  const bad = ["<", ">", '"', "'", "`", "${", "{{", "javascript:", "data:"];
  for (const p of bad) {
    if (value.includes(p)) return `Invalid character or pattern: ${p}`;
  }
  return null;
}

function validateOrigins(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) return "Origins are required";
  if (trimmed === "*") return null;
  const parts = trimmed.split(",").map((s) => s.trim());
  for (const part of parts) {
    if (part !== "*" && !/^https?:\/\//.test(part)) {
      return `Invalid origin: "${part}" — must be * or start with http(s)://`;
    }
  }
  return null;
}

function SaveIndicator({ status }: { status: SaveStatus }) {
  if (status === "idle" || status === "saving") return null;
  return (
    <span
      role="status"
      className={`save-status ${status === "saved" ? "save-status-saved" : "save-status-error"}`}
    >
      {status === "saved" ? "✓ Saved" : "⚠ Save failed"}
    </span>
  );
}

function ResetButton({
  field,
  isChanged,
  onReset,
}: {
  field: keyof LocalSettings;
  isChanged: boolean;
  onReset: (key: keyof LocalSettings) => void;
}) {
  if (!isChanged) return null;
  return (
    <button
      className="reset-btn"
      onClick={() => onReset(field)}
      title="Reset to default"
      aria-label={`Reset ${field} to default`}
    >
      ↺
    </button>
  );
}

/* --- Descriptions for each field (#19) --- */

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

/** Stacked text input with validation, reset button, and error display. */
function ValidatedTextInput({
  field,
  id,
  label,
  description,
  value,
  validate,
  error,
  setError,
  isChanged,
  onSave,
  onReset,
}: {
  field: keyof LocalSettings;
  id: string;
  label: string;
  description: string;
  value: string;
  validate: (v: string) => string | null;
  error: string | null;
  setError: (e: string | null) => void;
  isChanged: boolean;
  onSave: (v: string) => void;
  onReset: (k: keyof LocalSettings) => void;
}) {
  return (
    <div className="setting-row setting-row-stacked">
      <SettingLabel label={label} description={description} id={id} />
      <div className="input-with-reset">
        <input
          className={`input ${error ? "input-error" : ""}`}
          type="text"
          value={value}
          aria-labelledby={`${id}-label`}
          aria-describedby={error ? `${id}-error` : `${id}-desc`}
          aria-invalid={!!error}
          onChange={(e) => {
            const v = e.target.value;
            const err = validate(v);
            setError(err);
            if (!err) onSave(v);
          }}
        />
        <ResetButton
          field={field}
          isChanged={isChanged}
          onReset={(k) => {
            onReset(k);
            setError(null);
          }}
        />
      </div>
      {error && (
        <span className="error-text" id={`${id}-error`}>{error}</span>
      )}
    </div>
  );
}

export default function Settings() {
  const [status, setStatus] = useState<CacheStatus | null>(null);
  const [settings, setSettings] = useState<ServerSettings | null>(null);
  const [error, setError] = useState("");
  const { getValue, setValue, isChanged, resetValue, saveStatus } =
    useLocalSettings(settings);

  const [urlError, setUrlError] = useState<string | null>(null);
  const [corsError, setCorsError] = useState<string | null>(null);

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
        <h2>
          Server Settings &amp; Status
          <SaveIndicator status={saveStatus} />
        </h2>
        <p>Cache health, configuration, and API access</p>
      </div>

      {/* --- Cache Status (read-only) --- */}
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

      {/* --- Configuration (editable) --- */}
      <div className="card section-gap">
        <div className="card-section-title">Configuration</div>
        <div className="settings-grid">
          {/* Cache Interval — dropdown */}
          <div className="setting-row">
            <SettingLabel
              label="Cache Interval"
              description={CONFIG_DESCRIPTIONS.cache_interval_minutes}
              id="cfg-interval"
            />
            <span className="setting-value">
              <select
                className="input"
                value={getValue("cache_interval_minutes") ?? settings.cache_interval_minutes}
                aria-labelledby="cfg-interval-label"
                aria-describedby="cfg-interval-desc"
                onChange={(e) =>
                  setValue("cache_interval_minutes", Number(e.target.value))
                }
              >
                {CACHE_INTERVAL_OPTIONS.map((m) => (
                  <option key={m} value={m}>
                    {formatInterval(m)}
                  </option>
                ))}
              </select>
              <ResetButton
                field="cache_interval_minutes"
                isChanged={isChanged("cache_interval_minutes")}
                onReset={resetValue}
              />
            </span>
          </div>

          {/* Auth Enabled — read-only */}
          <div className="setting-row">
            <SettingLabel
              label="Auth Enabled"
              description={CONFIG_DESCRIPTIONS.auth_enabled}
              id="cfg-auth"
            />
            <span className="setting-value">
              {settings.auth_enabled ? "Yes" : "No"}
            </span>
          </div>

          {/* MCP Server — segmented control */}
          <div className="setting-row">
            <SettingLabel
              label="MCP Server"
              description={CONFIG_DESCRIPTIONS.mcp_enabled}
              id="cfg-mcp"
            />
            <span className="setting-value">
              <div
                className="segmented-control"
                role="radiogroup"
                aria-labelledby="cfg-mcp-label"
              >
                <label>
                  <input
                    type="radio"
                    name="mcp_enabled"
                    checked={getValue("mcp_enabled") === true}
                    onChange={() => setValue("mcp_enabled", true)}
                  />
                  <span>Enabled</span>
                </label>
                <label>
                  <input
                    type="radio"
                    name="mcp_enabled"
                    checked={getValue("mcp_enabled") === false}
                    onChange={() => setValue("mcp_enabled", false)}
                  />
                  <span>Disabled</span>
                </label>
              </div>
              <ResetButton
                field="mcp_enabled"
                isChanged={isChanged("mcp_enabled")}
                onReset={resetValue}
              />
            </span>
          </div>

          {/* Log Level — dropdown */}
          <div className="setting-row">
            <SettingLabel
              label="Log Level"
              description={CONFIG_DESCRIPTIONS.log_level}
              id="cfg-loglevel"
            />
            <span className="setting-value">
              <select
                className="input"
                value={getValue("log_level") ?? settings.log_level}
                aria-labelledby="cfg-loglevel-label"
                aria-describedby="cfg-loglevel-desc"
                onChange={(e) => setValue("log_level", e.target.value)}
              >
                {LOG_LEVEL_OPTIONS.map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
              <ResetButton
                field="log_level"
                isChanged={isChanged("log_level")}
                onReset={resetValue}
              />
            </span>
          </div>

          {/* NOAA Base URL — stacked text input */}
          <ValidatedTextInput
            field="noaa_base_url"
            id="cfg-noaa"
            label="NOAA Base URL"
            description={CONFIG_DESCRIPTIONS.noaa_base_url}
            value={(getValue("noaa_base_url") ?? settings.noaa_base_url) as string}
            validate={validateUrl}
            error={urlError}
            setError={setUrlError}
            isChanged={isChanged("noaa_base_url")}
            onSave={(v) => setValue("noaa_base_url", v)}
            onReset={resetValue}
          />

          {/* CORS Origins — stacked text input */}
          <ValidatedTextInput
            field="allowed_origins"
            id="cfg-cors"
            label="CORS Origins"
            description={CONFIG_DESCRIPTIONS.allowed_origins}
            value={(getValue("allowed_origins") ?? settings.allowed_origins.join(", ")) as string}
            validate={validateOrigins}
            error={corsError}
            setError={setCorsError}
            isChanged={isChanged("allowed_origins")}
            onSave={(v) => setValue("allowed_origins", v)}
            onReset={resetValue}
          />
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
