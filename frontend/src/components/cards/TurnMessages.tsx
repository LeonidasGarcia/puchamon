import { useEffect, useState } from 'react';
import type { BattleTurnEvent } from '../../types/schemas/Battle';
import TurnEvent from './TurnEvent';

interface TurnMessagesProps {
  turnNumber: number;
  events: BattleTurnEvent[];
  currentEventIndex: number;
  isAnimating: boolean;
}

const EVENT_ANIMATION_DELAY_MS = 500;

export default function TurnMessages({
  turnNumber,
  events,
  currentEventIndex,
  isAnimating,
}: TurnMessagesProps) {
  const [canAnimate, setCanAnimate] = useState(false);

  useEffect(() => {
    if (isAnimating && currentEventIndex === 0 && !canAnimate) {
      const timer = setTimeout(() => {
        setCanAnimate(true);
      }, EVENT_ANIMATION_DELAY_MS);
      return () => clearTimeout(timer);
    } else if (!isAnimating) {
      setCanAnimate(false);
    }
  }, [isAnimating, currentEventIndex, canAnimate]);

  const visibleEvents = events.slice(0, currentEventIndex + 1);

  return (
    <div className="flex flex-col gap-1 py-2">
      <span className="text-white font-bold text-h2">Turno {turnNumber}</span>
      <div className="flex flex-col gap-0.5 pl-2">
        {visibleEvents.map((event, index) => (
          <TurnEvent
            key={`${turnNumber}-${event.order}-${index}`}
            event={event}
            isAnimating={
              canAnimate &&
              isAnimating &&
              index === currentEventIndex
            }
          />
        ))}
      </div>
    </div>
  );
}