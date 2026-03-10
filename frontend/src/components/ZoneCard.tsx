import { useSortable } from "@dnd-kit/sortable";
import { Link } from "react-router-dom";
import type { ZoneForecast } from "../api";
import { AdvisoryBadges } from "./AdvisoryBadges";

interface Props {
  forecast: ZoneForecast;
  isPinned: boolean;
  onTogglePin: (zoneId: string) => void;
}

export function ZoneCard({ forecast: f, isPinned, onTogglePin }: Props) {
  const { attributes, listeners, setNodeRef, isDragging } = useSortable({
    id: f.zone_id,
  });

  const cardClass = [
    "card",
    f.has_active_advisory ? "card-danger" : f.has_upcoming_advisory ? "card-advisory" : "",
    isDragging ? "card-dragging" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div ref={setNodeRef} className="card-link">
      <div className={cardClass}>
        <div className="card-header">
          <div className="card-header-left">
            <span
              className="drag-handle"
              {...attributes}
              {...listeners}
              role="button"
              tabIndex={0}
              aria-roledescription="sortable"
              aria-label={`Drag to reorder ${f.zone_name}`}
            >
              ⠿
            </span>
            <span className="card-title">{f.zone_name}</span>
          </div>
          <div className="card-header-right">
            <button
              className="pin-btn"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onTogglePin(f.zone_id);
              }}
              aria-pressed={isPinned}
              aria-label={isPinned ? "Unpin zone" : "Pin zone"}
              title={isPinned ? "Unpin" : "Pin to top"}
            >
              {isPinned ? "📌" : "📍"}
            </button>
            <span className="setting-value">{f.zone_id}</span>
          </div>
        </div>
        <Link to={`/zone/${f.zone_id}`} className="card-body-link">
          <AdvisoryBadges forecast={f} />
          {f.advisory_text && (
            <div className="advisory-text">{f.advisory_text}</div>
          )}
          <div className="forecast-text forecast-preview">{f.forecast_text}</div>
        </Link>
      </div>
    </div>
  );
}
