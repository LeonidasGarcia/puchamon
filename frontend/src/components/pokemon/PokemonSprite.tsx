import { motion, scale, useAnimation, type Variants } from 'motion/react';
import { PokemonAnimationState, useGameStore } from '../../stores/gameStore';
import { useEffect } from 'react';

interface PokemonSpriteProps {
  name?: string;
  sprite: string | undefined;
  instanceId?: string;
  instanceIds?: string[];
  trainerId?: string;
  direction?: 'left' | 'right';
  isFainted?: boolean;
}

export default function PokemonSprite(props: PokemonSpriteProps) {
  const controls = useAnimation();

  // animación a renderizar según el estado
  const { animationStates, toIdle } = useGameStore();

  const animationState = animationStates[props.instanceId];

  const animationVariants: Record<PokemonAnimationState, Variants[string]> = {
    attacking: {
      x: props.direction === 'left' ? [0, -30, 0] : [0, 30, 0],
      y: props.direction === 'left' ? [0, 20, 0] : [0, -20, 0],
      transition: {
        ease: 'easeInOut',
        duration: 0.6,
        times: [0, 0.2, 1],
      },
    },
    takingDamage: {
      opacity: [1, 0, 1, 0, 1],
      transition: { duration: 1 },
    },
    fainted: {
      opacity: 0,
      transition: { duration: 1 },
    },
    idle: {
      x: 0,
      y: 0,
    },
    paralyzedEffect: {
      rotate: [0, 10, -10, 10, -10, 0],
      transition: { duration: 1 },
    },
    switchingIn: {
      opacity: [0, 1],
      transition: { duration: 1 },
    },
    switchingOut: {
      opacity: [1, 0],
      transition: { duration: 1 },
    },
    toxicEffect: {
      opacity: [1, 0.5, 1, 0.5, 1],
      transition: { duration: 1 },
    },
  };

  const playAnimation = async (state: PokemonAnimationState) => {
    await controls.start(state);
  };

  console.log(animationState);

  useEffect(() => {
    (async () => {
      await playAnimation(animationState);
      toIdle(props.instanceId);
    })();
  }, [animationState]);

  return (
    <div className="relative z-50">
      <motion.img
        className="relative inline-block h-fit"
        animate={controls}
        variants={animationVariants}
        initial={PokemonAnimationState.Idle}
        style={{
          scale: 2,
          transformOrigin: 'center bottom',
          zIndex: 50,
        }}
        src={props.sprite}
        alt={props.name}
      />
    </div>
  );
}
