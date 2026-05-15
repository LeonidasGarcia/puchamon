import { motion } from 'framer-motion';
import {
  getEventKindColor,
  type EventKindColorsKeys,
} from '../../types/colors/EventKindColors';
import type { BattleTurnEvent } from '../../types/schemas/Battle';

interface TurnEventProps {
  event: BattleTurnEvent;
  isAnimating?: boolean;
}

export default function TurnEvent({ event, isAnimating }: TurnEventProps) {
  const color = getEventKindColor(event.kind as EventKindColorsKeys);
  const isFainted = event.kind === 'pokemon_fainted';
  const isBattleFinished = event.kind === 'battle_finished';

  return (
    <motion.p
      className={`text-body leading-tight ${isFainted ? 'line-through' : ''} ${isBattleFinished ? 'font-bold' : ''}`}
      style={{ color }}
      initial={isAnimating ? { opacity: 0, x: -10 } : { opacity: 1, x: 0 }}
      animate={{ opacity: 1, x: 0 }}
      transition={isAnimating ? { duration: 0.3 } : { duration: 0 }}
    >
      {event.message}
    </motion.p>
  );
}
