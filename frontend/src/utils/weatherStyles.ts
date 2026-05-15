import {
  getWeatherColor,
  type WeatherColorsKeys,
} from '../types/colors/WeatherColors';

export function blendWeatherWithWhite(
  weatherId: WeatherColorsKeys | null,
  intensity: number = 0.15,
): string {
  if (!weatherId) return '#DBDBBE';

  const weatherColor = getWeatherColor(weatherId);
  const r = parseInt(weatherColor.slice(1, 3), 16);
  const g = parseInt(weatherColor.slice(3, 5), 16);
  const b = parseInt(weatherColor.slice(5, 7), 16);
  const whiteR = 219;
  const whiteG = 219;
  const whiteB = 190;
  const blendedR = Math.round(whiteR + (r - whiteR) * intensity);
  const blendedG = Math.round(whiteG + (g - whiteG) * intensity);
  const blendedB = Math.round(whiteB + (b - whiteB) * intensity);
  return `rgb(${blendedR}, ${blendedG}, ${blendedB})`;
}

export function getWeatherShadowColor(
  weatherId: WeatherColorsKeys | null,
): string {
  if (!weatherId) return '0 0 32px rgba(255,255,255,0.5)';

  const weatherColor = getWeatherColor(weatherId);
  const r = parseInt(weatherColor.slice(1, 3), 16);
  const g = parseInt(weatherColor.slice(3, 5), 16);
  const b = parseInt(weatherColor.slice(5, 7), 16);

  return `0 0 32px rgba(${r}, ${g}, ${b}, 0.5)`;
}
