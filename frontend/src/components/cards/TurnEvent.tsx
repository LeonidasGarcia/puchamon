import { forwardRef } from 'react'; // Importante
import { motion } from 'motion/react';
import {
  getEventKindColor,
  type EventKindColorsKeys,
} from '../../types/colors/EventKindColors';
import type { BattleTurnEvent } from '../../types/schemas/Battle';

interface TurnEventProps {
  event: BattleTurnEvent;
}

// Usamos forwardRef para que motion pueda controlar el elemento <p>
const TurnEvent = forwardRef<HTMLParagraphElement, TurnEventProps>(
  ({ event, ...props }, ref) => {
    // Extraemos event y capturamos el resto en ...props
    const color = getEventKindColor(event.kind as EventKindColorsKeys);
    const isFainted = event.kind === 'pokemon_fainted';
    const isBattleFinished = event.kind === 'battle_finished';
    return (
      <p
        {...props} // IMPORTANTE: Aquí pasan las variants, el style de la animación, etc.
        ref={ref} // IMPORTANTE: Aquí se conecta la animación al DOM
        className={`text-body leading-tight ${isFainted ? 'line-through' : ''} ${isBattleFinished ? 'font-bold' : ''}`}
        style={{ color }} // Combinamos el estilo de motion con tu color
      >
        {event.message}
      </p>
    );
  },
);

export default motion(TurnEvent);
