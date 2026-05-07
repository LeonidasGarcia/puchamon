import type { BattleTurnEvent } from '../../types/schemas/Battle';
import TurnEvent from './TurnEvent';

interface TurnMessagesProps {
  turnNumber: number;
  events: BattleTurnEvent[];
}

export default function TurnMessages({
  turnNumber,
  events,
}: TurnMessagesProps) {
  return (
    <div className="flex flex-col gap-1 py-2">
      <span className="text-white font-bold text-h2">Turno {turnNumber}</span>
      <div className="flex flex-col gap-0.5 pl-2">
        {events.map((event, index) => (
          <TurnEvent
            key={`${turnNumber}-${event.order}-${index}`}
            event={event}
          />
        ))}
      </div>
    </div>
  );
}
