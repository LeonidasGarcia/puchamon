import { blendWeatherWithWhite } from '../../utils/weatherStyles';
import type { WeatherColorsKeys } from '../../types/colors/WeatherColors';

interface GroundProps {
  weatherId?: WeatherColorsKeys | null;
}

export default function Ground(props: GroundProps & React.HTMLAttributes<HTMLDivElement>) {
  const backgroundColor = props.weatherId
    ? blendWeatherWithWhite(props.weatherId, 0.15)
    : '#B2B293';

  const borderColor = props.weatherId
    ? blendWeatherWithWhite(props.weatherId, 0.45)
    : '#C9C7B2';

  return (
    <div
      {...props}
      className={`w-68 h-16 ${props.className}`}
      style={{
        ...props.style,
        backgroundColor,
        borderColor,
        borderWidth: 6,
        borderStyle: 'solid',
        borderRadius: '50%',
      }}
    />
  );
}
