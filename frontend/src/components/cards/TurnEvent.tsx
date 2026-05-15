import {
  getEventKindColor,
  type EventKindColorsKeys,
} from '../../types/colors/EventKindColors';
import type { BattleTurnEvent } from '../../types/schemas/Battle';

interface TurnEventProps {
  event: BattleTurnEvent;
}

export default function TurnEvent({ event }: TurnEventProps) {
  const color = getEventKindColor(event.kind as EventKindColorsKeys);
  const isFainted = event.kind === 'pokemon_fainted';
  const isBattleFinished = event.kind === 'battle_finished';

  return (
    <p
      className={`text-body leading-tight ${isFainted ? 'line-through' : ''} ${isBattleFinished ? 'font-bold' : ''}`}
      style={{ color }}
    >
      {event.message}
    </p>
  );
}