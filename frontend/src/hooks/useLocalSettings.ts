import { useCallback, useEffect, useRef, useState } from "react";
import type { ServerSettings } from "../api";

const STORAGE_KEY = "user_settings";
const DEBOUNCE_MS = 500;

/** Only these keys can be overridden by the user. */
const VALID_KEYS: (keyof LocalSettings)[] = [
  "cache_interval_minutes",
  "mcp_enabled",
  "log_level",
  "noaa_base_url",
  "allowed_origins",
];

export interface LocalSettings {
  cache_interval_minutes?: number;
  mcp_enabled?: boolean;
  log_level?: string;
  noaa_base_url?: string;
  allowed_origins?: string;
}

function readStored(): LocalSettings {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    // Strip stale keys that don't exist in the current schema
    const cleaned: LocalSettings = {};
    for (const key of VALID_KEYS) {
      if (key in parsed) (cleaned as Record<string, unknown>)[key] = parsed[key];
    }
    return cleaned;
  } catch {
    return {};
  }
}

function writeStored(overrides: LocalSettings): boolean {
  try {
    const cleaned = Object.fromEntries(
      Object.entries(overrides).filter(([, v]) => v !== undefined),
    );
    if (Object.keys(cleaned).length === 0) {
      localStorage.removeItem(STORAGE_KEY);
    } else {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(cleaned));
    }
    return true;
  } catch {
    return false;
  }
}

export type SaveStatus = "idle" | "saving" | "saved" | "error";

/** Merged view of server defaults + user localStorage overrides with debounced auto-save. */
export function useLocalSettings(serverDefaults: ServerSettings | null) {
  const [overrides, setOverrides] = useState<LocalSettings>(readStored);
  const [saveStatus, setSaveStatus] = useState<SaveStatus>("idle");
  const timerRef = useRef<ReturnType<typeof setTimeout>>(null);
  const flashRef = useRef<ReturnType<typeof setTimeout>>(null);
  const isFirstRender = useRef(true);

  // Debounced persist to localStorage
  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    setSaveStatus("saving");
    timerRef.current = setTimeout(() => {
      const ok = writeStored(overrides);
      setSaveStatus(ok ? "saved" : "error");
      flashRef.current = setTimeout(() => setSaveStatus("idle"), 2000);
    }, DEBOUNCE_MS);

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      if (flashRef.current) clearTimeout(flashRef.current);
    };
  }, [overrides]);

  const getValue = useCallback(
    <K extends keyof LocalSettings>(key: K): LocalSettings[K] | undefined => {
      if (overrides[key] !== undefined) return overrides[key];
      if (!serverDefaults) return undefined;
      if (key === "allowed_origins") {
        return serverDefaults.allowed_origins.join(", ") as LocalSettings[K];
      }
      return serverDefaults[key as keyof ServerSettings] as LocalSettings[K];
    },
    [overrides, serverDefaults],
  );

  const isChanged = useCallback(
    (key: keyof LocalSettings): boolean => {
      if (overrides[key] === undefined) return false;
      if (!serverDefaults) return false;
      if (key === "allowed_origins") {
        return overrides[key] !== serverDefaults.allowed_origins.join(", ");
      }
      return overrides[key] !== serverDefaults[key as keyof ServerSettings];
    },
    [overrides, serverDefaults],
  );

  const setValue = useCallback(
    <K extends keyof LocalSettings>(key: K, value: LocalSettings[K]) => {
      setOverrides((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const resetValue = useCallback((key: keyof LocalSettings) => {
    setOverrides((prev) => {
      const next = { ...prev };
      delete next[key];
      return next;
    });
  }, []);

  return { getValue, setValue, isChanged, resetValue, saveStatus };
}
