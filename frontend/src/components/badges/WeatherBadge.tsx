import {
  getWeatherColor,
  type WeatherColorsKeys,
} from '../../types/colors/WeatherColors';

interface WeatherBadgeProps {
  weatherId: WeatherColorsKeys;
  remainingTurns: number;
}

export default function WeatherBadge({
  weatherId,
  remainingTurns,
}: WeatherBadgeProps) {
  const weatherColor = getWeatherColor(weatherId);
  const weatherName = weatherId.charAt(0).toUpperCase() + weatherId.slice(1);

  return (
    <div className="absolute top-2 left-2 z-10 flex flex-row items-center gap-4">
      <div
        className="px-4 rounded-lg text-body font-bold text-white shadow-md"
        style={{ backgroundColor: weatherColor }}
      >
        {weatherName}
      </div>
      <span className="text-small font-medium text-[--color-text-primary]">
        {remainingTurns} turnos
      </span>
    </div>
  );
}
