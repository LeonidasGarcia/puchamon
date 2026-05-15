import { useRef, useEffect } from 'react';
import type { BattleTurnDTO } from '../../types/schemas/Battle';
import TurnMessages from '../../components/cards/TurnMessages';

interface TurnLogProps {
  turns: BattleTurnDTO[];
  isAnimating?: boolean;
  currentEventIndex?: number;
}

export default function TurnLog({
  turns,
  isAnimating,
  currentEventIndex,
}: TurnLogProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [turns, currentEventIndex]);

  const lastTurn = turns[turns.length - 1];

  if (turns.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <span className="text-white text-body">Sin eventos aún</span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="flex flex-col gap-2 overflow-y-auto w-full max-h-170 pr-2"
    >
      {turns.map((turn) => (
        <TurnMessages
          key={turn.turn}
          turnNumber={turn.turn}
          events={turn.events}
          isAnimating={isAnimating && turn === lastTurn}
          currentEventIndex={currentEventIndex}
        />
      ))}
    </div>
  );
}
