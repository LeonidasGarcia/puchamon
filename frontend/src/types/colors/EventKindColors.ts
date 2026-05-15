export const EVENT_KIND_COLORS = {
  move: "#e5e5e5",
  damage: "#ef4444",
  pokemon_fainted: "#9ca3af",
  switch: "#93c5fd",
  weather_ended: "#7dd3fc",
  battle_finished: "#FFD700",
  weather_started: "#7dd3fc",
  hazard_set: "#fcd34d",
  hazard_removed: "#fdba74",
  stat_change: "#c4b5fd",
  status_applied: "#f9a8d4",
  status_removed: "#86efac",
  default: "#e5e5e5",
};

export type EventKindColorsKeys = keyof typeof EVENT_KIND_COLORS;

export function getEventKindColor(kind: EventKindColorsKeys): string {
  return EVENT_KIND_COLORS[kind] ?? EVENT_KIND_COLORS.default;
}