import { useRef, useEffect } from 'react';
import type { BattleTurnDTO } from '../../types/schemas/Battle';
import TurnMessages from '../../components/cards/TurnMessages';

interface TurnLogProps {
  turns: BattleTurnDTO[];
}

export default function TurnLog({ turns }: TurnLogProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [turns]);

  if (turns.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <span className="text-[--color-text-secondary] text-text">
          Sin eventos aún
        </span>
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
        />
      ))}
    </div>
  );
}
