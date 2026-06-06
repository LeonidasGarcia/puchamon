import { useRef, useEffect } from 'react';
import TurnMessages from '../../components/cards/TurnMessages';
import { useGameStore } from '../../stores/gameStore';

export default function TurnLog() {
  const { turnHistory } = useGameStore();
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [turnHistory]);

  if (turnHistory.length === 0) {
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
      {turnHistory.map((turn, index) => {
        const showHeader =
          index === 0 || turnHistory[index - 1].turn !== turn.turn;
        return (
          <TurnMessages
            key={`history-${turn.turn}-${index}`}
            turnNumber={turn.turn}
            events={turn.events}
            showHeader={showHeader}
          />
        );
      })}
    </div>
  );
}