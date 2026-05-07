import { motion } from 'framer-motion';
import Ground from './Ground';
import PokemonSprite from '../pokemon/PokemonSprite';
import WeatherBadge from '../badges/WeatherBadge';
import HazardBadge from '../badges/HazardBadge';
import {
  blendWeatherWithWhite,
  getWeatherShadowColor,
} from '../../utils/weatherStyles';
import type PokemonSprites from '../../types/sprites/PokemonSprites';
import type { WeatherColorsKeys } from '../../types/colors/WeatherColors';
import type { HazardColorsKeys } from '../../types/colors/HazardColors';
import type {
  PokemonInstanceSnapshot,
  BattleTurnEvent,
} from '../../types/schemas/Battle';

interface BattleScenarioProps {
  p1Sprites: PokemonSprites[];
  p2Sprites: PokemonSprites[];
  weatherId?: WeatherColorsKeys | null;
  weatherRemainingTurns?: number | null;
  hazards?: HazardColorsKeys[];
  isAnimating?: boolean;
  currentEventIndex?: number;
  currentEvents?: BattleTurnEvent[];
  myPokemon?: PokemonInstanceSnapshot[];
  opponentPokemon?: PokemonInstanceSnapshot[];
}

export default function BattleScenario(props: BattleScenarioProps) {
  const backgroundColor = blendWeatherWithWhite(props.weatherId ?? null, 0.15);
  const shadowColor = getWeatherShadowColor(props.weatherId ?? null);

  return (
    <motion.div
      className="w-240 h-135 p-8 m-8 rounded-3xl grid grid-rows-2 grid-cols-2"
      style={{ backgroundColor, boxShadow: shadowColor }}
      transition={{ duration: 0.5, ease: 'easeInOut' }}
      animate={{ backgroundColor, boxShadow: shadowColor }}
    >
      <div className="relative flex flex-col gap-1">
        {props.weatherId && props.weatherRemainingTurns !== null && (
          <WeatherBadge
            weatherId={props.weatherId}
            remainingTurns={props.weatherRemainingTurns}
          />
        )}
        {props.hazards && props.hazards.length > 0 && (
          <div className="absolute top-16 left-2 z-10 flex gap-3">
            {props.hazards.map((hazardId) => (
              <HazardBadge key={hazardId} hazardId={hazardId} />
            ))}
          </div>
        )}
      </div>
      <div className="relative flex w-64 h-16 flex-start self-end items-end justify-center py-4">
        <Ground weatherId={props.weatherId} className="absolute z-0 top-1" />
        {props.p2Sprites.map((sprite, idx) => (
          <PokemonSprite
            key={props.opponentPokemon?.[idx]?.instance_id ?? idx}
            sprite={sprite?.normal}
            isAnimating={props.isAnimating}
            currentEventIndex={props.currentEventIndex}
            currentEvents={props.currentEvents}
            instanceId={props.opponentPokemon?.[idx]?.instance_id}
            instanceIds={props.opponentPokemon?.map((p) => p.instance_id) ?? []}
            trainerId={props.opponentPokemon?.[idx]?.trainer_id}
            direction="left"
          />
        ))}
      </div>
      <div className="relative flex w-64 h-16 flex-start self-end justify-self-end items-end justify-center py-6">
        <Ground weatherId={props.weatherId} className="absolute z-0 top-0.5" />
        {props.p1Sprites.map((sprite, idx) => (
          <PokemonSprite
            key={props.myPokemon?.[idx]?.instance_id ?? idx}
            sprite={sprite?.back_normal}
            isAnimating={props.isAnimating}
            currentEventIndex={props.currentEventIndex}
            currentEvents={props.currentEvents}
            instanceId={props.myPokemon?.[idx]?.instance_id}
            instanceIds={props.myPokemon?.map((p) => p.instance_id) ?? []}
            trainerId={props.myPokemon?.[idx]?.trainer_id}
            direction="right"
          />
        ))}
      </div>
      <div></div>
    </motion.div>
  );
}
