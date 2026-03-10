import { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import { api } from "../api";
import type { AllForecastsResponse, CacheStatus, ZoneForecast } from "../api";
import { fmtTime, timeAgo } from "../utils/time";
import { ZoneCard } from "../components/ZoneCard";
import { SkeletonCards } from "../components/SkeletonCards";
import { FailedZoneCard } from "../components/FailedZoneCard";
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import type { DragEndEvent } from "@dnd-kit/core";
import { SortableContext, sortableKeyboardCoordinates } from "@dnd-kit/sortable";

function loadPinned(): string[] {
  try {
    return JSON.parse(localStorage.getItem("pinned_zones") || "[]");
  } catch {
    return [];
  }
}

function loadOrder(): string[] {
  try {
    return JSON.parse(localStorage.getItem("zone_order") || "[]");
  } catch {
    return [];
  }
}

function savePinned(pinned: string[]) {
  localStorage.setItem("pinned_zones", JSON.stringify(pinned));
}

function saveOrder(order: string[]) {
  localStorage.setItem("zone_order", JSON.stringify(order));
}

function buildOrderedForecasts(
  forecasts: ZoneForecast[],
  pinned: string[],
  savedOrder: string[],
): ZoneForecast[] {
  const byId = new Map(forecasts.map((f) => [f.zone_id, f]));

  // Start with saved order, then append any zones not in the saved order
  const ordered: ZoneForecast[] = [];
  for (const id of savedOrder) {
    const f = byId.get(id);
    if (f) {
      ordered.push(f);
      byId.delete(id);
    }
  }
  for (const f of forecasts) {
    if (byId.has(f.zone_id)) {
      ordered.push(f);
    }
  }

  // Split into pinned and unpinned, preserving relative order
  const pinnedSet = new Set(pinned);
  const pinnedItems = ordered.filter((f) => pinnedSet.has(f.zone_id));
  const unpinnedItems = ordered.filter((f) => !pinnedSet.has(f.zone_id));

  return [...pinnedItems, ...unpinnedItems];
}

export default function Dashboard() {
  const [data, setData] = useState<AllForecastsResponse | null>(null);
  const [status, setStatus] = useState<CacheStatus | null>(null);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [pinned, setPinned] = useState<string[]>(loadPinned);
  const [order, setOrder] = useState<string[]>(loadOrder);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

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
      toast.success("Forecasts updated");
    } catch (e: any) {
      setError(e.message);
      toast.error(`Refresh failed: ${e.message}`);
    } finally {
      setRefreshing(false);
    }
  };

  const togglePin = useCallback(
    (zoneId: string) => {
      const next = pinned.includes(zoneId)
        ? pinned.filter((id) => id !== zoneId)
        : [...pinned, zoneId];
      setPinned(next);
      savePinned(next);
    },
    [pinned],
  );

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      if (!over || active.id === over.id || !data) return;

      const forecasts = buildOrderedForecasts(data.forecasts, pinned, order);
      const ids = forecasts.map((f) => f.zone_id);
      const oldIndex = ids.indexOf(active.id as string);
      const newIndex = ids.indexOf(over.id as string);
      if (oldIndex === -1 || newIndex === -1) return;

      // Reorder
      const newIds = [...ids];
      newIds.splice(oldIndex, 1);
      newIds.splice(newIndex, 0, active.id as string);

      // If dragged into/out of pinned section, update pins
      const pinnedCount = pinned.length;
      const draggedId = active.id as string;
      const wasPinned = pinned.includes(draggedId);

      let newPinned = [...pinned];
      if (!wasPinned && newIndex < pinnedCount) {
        // Dragged into pinned section
        newPinned.push(draggedId);
      } else if (wasPinned && newIndex >= pinnedCount) {
        // Dragged out of pinned section
        newPinned = newPinned.filter((id) => id !== draggedId);
      }

      setPinned(newPinned);
      savePinned(newPinned);
      setOrder(newIds);
      saveOrder(newIds);
    },
    [data, pinned, order],
  );

  if (error && !data) return <div className="error-msg">Error: {error}</div>;
  if (!data)
    return (
      <>
        <div className="page-header">
          <h2>Marine Forecast Dashboard</h2>
          <p>Puget Sound &amp; Washington Coastal Waters</p>
        </div>
        <SkeletonCards count={6} />
      </>
    );

  const forecasts = buildOrderedForecasts(data.forecasts, pinned, order);
  const pinnedSet = new Set(pinned);
  const pinnedForecasts = forecasts.filter((f) => pinnedSet.has(f.zone_id));
  const unpinnedForecasts = forecasts.filter((f) => !pinnedSet.has(f.zone_id));
  const allIds = forecasts.map((f) => f.zone_id);

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
        <span
          aria-label={`Last updated ${fmtTime(data.cache_last_updated)}`}
          title={fmtTime(data.cache_last_updated)}
        >
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

      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={allIds}>
          {pinnedForecasts.length > 0 && (
            <>
              <div className="section-label">Pinned</div>
              <div className="zone-grid">
                {pinnedForecasts.map((f) => (
                  <ZoneCard
                    key={f.zone_id}
                    forecast={f}
                    isPinned={true}
                    onTogglePin={togglePin}
                  />
                ))}
              </div>
              <div className="pinned-divider" />
            </>
          )}

          <div className="zone-grid">
            {unpinnedForecasts.map((f) => (
              <ZoneCard
                key={f.zone_id}
                forecast={f}
                isPinned={false}
                onTogglePin={togglePin}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      {data.errors && data.errors.length > 0 && (
        <>
          <div className="section-label" style={{ color: "var(--danger)" }}>
            Failed Zones
          </div>
          <div className="zone-grid">
            {data.errors.map((e) => (
              <FailedZoneCard key={e.zone_id} zoneId={e.zone_id} error={e.error} />
            ))}
          </div>
        </>
      )}
    </>
  );
}
