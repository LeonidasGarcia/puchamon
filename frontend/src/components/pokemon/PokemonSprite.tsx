import { motion } from 'framer-motion';
import type { BattleTurnEvent } from '../../types/schemas/Battle';

interface PokemonSpriteProps {
  name?: string;
  sprite: string | undefined;
  isAnimating?: boolean;
  currentEventIndex?: number;
  currentEvents?: BattleTurnEvent[];
  instanceId?: string;
  instanceIds?: string[];
  trainerId?: string;
  direction?: 'left' | 'right';
}

export default function PokemonSprite(props: PokemonSpriteProps) {
  const shouldAnimate =
    props.isAnimating &&
    props.currentEvents &&
    props.currentEventIndex !== undefined &&
    props.instanceId &&
    props.currentEvents[props.currentEventIndex]?.source_instance_id ===
      props.instanceId;

  const dx = props.direction === 'left' ? -30 : 30;
  const dy = props.direction === 'left' ? 15 : -15;

  const hasFaintedEvent =
    props.currentEvents?.some(
      (e) =>
        e.kind === 'pokemon_fainted' &&
        e.source_instance_id === props.instanceId,
    ) ?? false;

  const isFaintAnimating =
    props.isAnimating && props.instanceId && hasFaintedEvent;

  return (
    <motion.div
      className="relative z-50"
      initial={{ x: 0, y: 0, opacity: 1, rotate: 0 }}
      animate={
        isFaintAnimating
          ? { x: 0, y: 20, opacity: 0, rotate: 90 }
          : shouldAnimate
            ? { x: [0, dx, 0], y: [0, dy, 0] }
            : { x: 0, y: 0 }
      }
      transition={
        isFaintAnimating
          ? { duration: 0.8, ease: 'easeIn' }
          : shouldAnimate
            ? { duration: 0.4, ease: 'easeOut' }
            : { duration: 0 }
      }
    >
      <img
        className="relative inline-block h-fit"
        style={{
          transform: 'scale(2)',
          transformOrigin: 'center bottom',
          zIndex: 50,
        }}
        src={props.sprite}
        alt={props.name}
      />
    </motion.div>
  );
}
