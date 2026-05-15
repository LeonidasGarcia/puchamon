import type { BattleTurnEvent } from '../../types/schemas/Battle';
import TurnEvent from './TurnEvent';

interface TurnMessagesProps {
  turnNumber: number;
  events: BattleTurnEvent[];
  isAnimating?: boolean;
  currentEventIndex?: number;
}

export default function TurnMessages({
  turnNumber,
  events,
  isAnimating,
  currentEventIndex,
}: TurnMessagesProps) {
  const visibleEvents = isAnimating
    ? events.slice(0, currentEventIndex + 1)
    : events;

  return (
    <div className="flex flex-col gap-1 py-2">
      <span className="text-white font-bold text-h2">Turno {turnNumber}</span>
      <div className="flex flex-col gap-0.5 pl-2">
        {visibleEvents.map((event, index) => (
          <TurnEvent
            key={`${turnNumber}-${event.order}-${index}`}
            event={event}
            isAnimating={isAnimating && index === currentEventIndex}
          />
        ))}
      </div>
    </div>
  );
}
