import { motion } from 'framer-motion';
import { blendWeatherWithWhite } from '../../utils/weatherStyles';
import type { WeatherColorsKeys } from '../../types/colors/WeatherColors';

interface GroundProps {
  weatherId?: WeatherColorsKeys | null;
}

export default function Ground(
  props: GroundProps & React.HTMLAttributes<HTMLDivElement>,
) {
  const backgroundColor = props.weatherId
    ? blendWeatherWithWhite(props.weatherId, 0.15)
    : '#B2B293';

  const borderColor = props.weatherId
    ? blendWeatherWithWhite(props.weatherId, 0.45)
    : '#C9C7B2';

  return (
    <div className={`flex w-68 h-16 ${props.className}`}>
      <motion.div
        className="flex-1 h-full border-6 box-border rounded-[50%/50%]"
        style={{ backgroundColor, borderColor }}
        transition={{ duration: 0.5, ease: 'easeInOut' }}
        animate={{ backgroundColor, borderColor }}
      ></motion.div>
    </div>
  );
}
