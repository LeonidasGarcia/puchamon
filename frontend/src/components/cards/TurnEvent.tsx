import { motion } from 'framer-motion';
import {
  getEventKindColor,
  type EventKindColorsKeys,
} from '../../types/colors/EventKindColors';
import type { BattleTurnEvent } from '../../types/schemas/Battle';
import { useGameStore } from '../../stores/gameStore';

interface TurnEventProps {
  event: BattleTurnEvent;
  isAnimating: boolean;
}

const EVENT_ANIMATION_DURATION = 0.3;

export default function TurnEvent({ event, isAnimating }: TurnEventProps) {
  const color = getEventKindColor(event.kind as EventKindColorsKeys);
  const isFainted = event.kind === 'pokemon_fainted';
  const isBattleFinished = event.kind === 'battle_finished';

  const handleAnimationComplete = () => {
    if (isAnimating) {
      useGameStore.getState().onEventComplete();
    }
  };

  return (
    <motion.p
      className={`text-body leading-tight ${isFainted ? 'line-through' : ''} ${isBattleFinished ? 'font-bold' : ''}`}
      style={{ color }}
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: EVENT_ANIMATION_DURATION, ease: 'easeOut' }}
      onAnimationComplete={handleAnimationComplete}
    >
      {event.message}
    </motion.p>
  );
}