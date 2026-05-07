export const WEATHER_COLORS = {
  rain: '#5B9BD5',
  sun: '#F5A623',
  sandstorm: '#C4A35A',
  hail: '#87CEEB',
};

export type WeatherColorsKeys = keyof typeof WEATHER_COLORS;

export function getWeatherColor(weatherId: WeatherColorsKeys): string {
  return WEATHER_COLORS[weatherId] ?? '#5B9BD5';
}
