import { useGameStore } from '../../stores/gameStore';
import type { BattleTurnEvent } from '../../types/schemas/Battle';
import TurnEvent from './TurnEvent';
import { motion, type Variants } from 'motion/react';

interface TurnMessagesProps {
  turnNumber: number;
  events: BattleTurnEvent[];
  showHeader?: boolean;
}

const containerVariants: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      // Espera 0.5s antes de iniciar la secuencia
      delayChildren: 0,
      // Cada hijo aparecerá con 0.3s de diferencia respecto al anterior
      staggerChildren: 3,
    },
  },
};

const eventVariants: Variants = {
  hidden: {
    opacity: 0,
    x: -20,
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      ease: 'easeInOut',
      stiffness: 120,
    },
  },
};

export default function TurnMessages({
  turnNumber,
  events,
  showHeader = true,
}: TurnMessagesProps) {
  const { applyEventKind, finalizeTurnAnimation } = useGameStore();

  return (
    <div className="flex flex-col gap-1 py-2">
      {showHeader && (
        <span className="text-white font-bold text-h2">Turno {turnNumber}</span>
      )}
      <motion.div
        onAnimationComplete={() => {
          finalizeTurnAnimation();
        }}
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="flex flex-col gap-0.5 pl-2"
      >
        {events.map((event, index) => (
          <TurnEvent
            key={`${turnNumber}-${event.order}-${index}`}
            event={event}
            onAnimationComplete={() => {
              applyEventKind(event);
            }}
            variants={eventVariants}
          />
        ))}
      </motion.div>
    </div>
  );
}
