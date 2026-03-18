import { useEffect, useState, useCallback } from "react";
import toast from "react-hot-toast";
import { api } from "../api";
import type { AllForecastsResponse, CacheStatus, ZoneForecast } from "../api";
import { fmtTime, timeAgo } from "../utils/time";
import { getZoneRegion, REGION_LABELS } from "../utils/zones";
import type { ZoneRegion } from "../utils/zones";
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
import { SortableContext, sortableKeyboardCoordinates, arrayMove } from "@dnd-kit/sortable";

function loadJson<T>(key: string, fallback: T): T {
  try {
    return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
  } catch {
    return fallback;
  }
}

function saveJson<T>(key: string, value: T) {
  localStorage.setItem(key, JSON.stringify(value));
}

const loadPinned = () => loadJson<string[]>("pinned_zones", []);
const loadOrder = () => loadJson<string[]>("zone_order", []);
const savePinned = (v: string[]) => saveJson("pinned_zones", v);
const saveOrder = (v: string[]) => saveJson("zone_order", v);

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

      const draggedId = active.id as string;
      const overId = over.id as string;

      const draggedPinned = pinned.includes(draggedId);
      const overPinned = pinned.includes(overId);

      // Cross-section: pin/unpin
      if (draggedPinned && !overPinned) {
        const newPinned = pinned.filter((id) => id !== draggedId);
        setPinned(newPinned);
        savePinned(newPinned);
        return;
      }
      if (!draggedPinned && overPinned) {
        const newPinned = [...pinned, draggedId];
        setPinned(newPinned);
        savePinned(newPinned);
        return;
      }

      // Same-section reorder: work with the section's own ID list
      const forecasts = buildOrderedForecasts(data.forecasts, pinned, order);
      const pinnedSet = new Set(pinned);

      let sectionIds: string[];
      if (draggedPinned) {
        sectionIds = forecasts.filter((f) => pinnedSet.has(f.zone_id)).map((f) => f.zone_id);
      } else {
        const region = getZoneRegion(draggedId);
        sectionIds = forecasts
          .filter((f) => !pinnedSet.has(f.zone_id) && getZoneRegion(f.zone_id) === region)
          .map((f) => f.zone_id);
      }

      const oldIndex = sectionIds.indexOf(draggedId);
      const newIndex = sectionIds.indexOf(overId);
      if (oldIndex === -1 || newIndex === -1) return;

      const reorderedSection = arrayMove(sectionIds, oldIndex, newIndex);

      // Rebuild the full order: replace the section's slice with reordered version
      const fullIds = forecasts.map((f) => f.zone_id);
      const sectionSet = new Set(sectionIds);
      const newFullIds: string[] = [];
      let sectionCursor = 0;
      for (const id of fullIds) {
        if (sectionSet.has(id)) {
          newFullIds.push(reorderedSection[sectionCursor++]);
        } else {
          newFullIds.push(id);
        }
      }

      setOrder(newFullIds);
      saveOrder(newFullIds);
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

  // Group unpinned forecasts by region
  const regionGroups: { region: ZoneRegion; items: ZoneForecast[] }[] = [];
  for (const region of ["salish-sea", "coastal"] as const) {
    const items = unpinnedForecasts.filter((f) => getZoneRegion(f.zone_id) === region);
    if (items.length > 0) regionGroups.push({ region, items });
  }

  // Build sortable ID lists: pinned IDs + each region's IDs (separate contexts)
  const pinnedIds = pinnedForecasts.map((f) => f.zone_id);

  return (
    <>
      <div className="page-header">
        <h2>Marine Forecast Dashboard</h2>
        <p>Puget Sound &amp; Washington Coastal Waters</p>
      </div>

      <div className="status-bar" aria-live="polite">
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
        {pinnedForecasts.length > 0 && (
          <>
            <div className="section-label">Pinned</div>
            <SortableContext items={pinnedIds}>
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
            </SortableContext>
            <div className="pinned-divider" />
          </>
        )}

        {regionGroups.map(({ region, items }) => (
          <div key={region}>
            <div className="section-label">{REGION_LABELS[region]}</div>
            <SortableContext items={items.map((f) => f.zone_id)}>
              <div className="zone-grid">
                {items.map((f) => (
                  <ZoneCard
                    key={f.zone_id}
                    forecast={f}
                    isPinned={false}
                    onTogglePin={togglePin}
                  />
                ))}
              </div>
            </SortableContext>
          </div>
        ))}
      </DndContext>

      {data.errors && data.errors.length > 0 && (
        <>
          <div className="section-label section-label-danger">
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
