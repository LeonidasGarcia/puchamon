import {
  getHazardColor,
  type HazardColorsKeys,
} from '../../types/colors/HazardColors';

interface HazardBadgeProps {
  hazardId: HazardColorsKeys;
}

export default function HazardBadge({ hazardId }: HazardBadgeProps) {
  const hazardColor = getHazardColor(hazardId);
  const hazardName = hazardId
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  return (
    <div
      className="px-3 py-1.5 rounded-lg text-text font-bold text-white shadow-md"
      style={{ backgroundColor: hazardColor }}
    >
      {hazardName}
    </div>
  );
}
