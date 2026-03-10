export type ZoneRegion = "salish-sea" | "coastal";

const SALISH_SEA_ZONES = new Set([
  "PZZ100",
  "PZZ110",
  "PZZ130",
  "PZZ131",
  "PZZ132",
  "PZZ133",
  "PZZ134",
  "PZZ135",
]);

export function getZoneRegion(zoneId: string): ZoneRegion {
  return SALISH_SEA_ZONES.has(zoneId) ? "salish-sea" : "coastal";
}

export const REGION_LABELS: Record<ZoneRegion, string> = {
  "salish-sea": "Salish Sea & Inland Waters",
  coastal: "Coastal Waters",
};
