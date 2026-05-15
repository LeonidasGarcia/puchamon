export const HAZARD_COLORS = {
  spikes: '#D4A017',
  'toxic-spikes': '#8B5CF6',
  'stealth-rock': '#C0C0C0',
  'sticky-web': '#10B981',
};

export type HazardColorsKeys = keyof typeof HAZARD_COLORS;

export function getHazardColor(hazardId: HazardColorsKeys): string {
  return HAZARD_COLORS[hazardId] ?? '#888888';
}
