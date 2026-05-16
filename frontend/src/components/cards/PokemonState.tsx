import { useState, useEffect, useRef } from 'react';
import { useMotionValue, animate } from 'framer-motion';
import HpBar from '../battle/HpBar';

interface PokemonStateProps {
  name: string;
  level: number;
  hpPercentage: number;
  currentHp: number;
  maxHp: number;
}

function AnimatedHpNumber({ value }: { value: number }) {
  const motionValue = useMotionValue(value);
  const [display, setDisplay] = useState(value);
  const animationRef = useRef<{ stop: () => void } | null>(null);

  useEffect(() => {
    animationRef.current = animate(motionValue, value, {
      duration: 0.5,
      ease: 'easeOut',
      onUpdate: (latest) => {
        setDisplay(Math.round(latest));
      },
    });

    return () => {
      animationRef.current?.stop();
    };
  }, [value, motionValue]);

  return <span>{display}</span>;
}

export default function PokemonState(props: PokemonStateProps) {
  return (
    <div className="flex bg-card-bg flex-col gap-2 px-2 py-2 rounded-lg border border-card-border min-w-52 shadow-sm">
      <div className="flex flex-row justify-between items-baseline">
        <span className="text-body font-medium text-[--color-text-primary] tracking-wide leading-none">
          {props.name}
        </span>
        <span className="text-small text-text-secondary font-medium leading-none">
          Lv. {props.level}
        </span>
      </div>
      <div className="flex flex-row items-center gap-3">
        <HpBar hpPercentage={props.hpPercentage} />
        <span className="text-hp-ratio text-text-secondary font-medium shrink-0 leading-none">
          <AnimatedHpNumber value={props.currentHp} />/{props.maxHp}
        </span>
      </div>
    </div>
  );
}