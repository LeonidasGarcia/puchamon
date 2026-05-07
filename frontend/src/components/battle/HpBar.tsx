import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  useMotionValueEvent,
} from 'framer-motion';
import { useEffect, useState } from 'react';

interface HpBarProps {
  hpPercentage: number;
}

export default function HpBar({ hpPercentage }: HpBarProps) {
  const motionHp = useMotionValue(hpPercentage);

  const springHp = useSpring(motionHp, {
    stiffness: 48,
    damping: 20,
    restDelta: 0.5,
  });

  const steppedHp = useTransform(springHp, (latest) => {
    const step = 0.5;
    return Math.round(latest / step) * step;
  });

  useEffect(() => {
    motionHp.set(hpPercentage);
  }, [hpPercentage, motionHp]);

  const [currentColor, setCurrentColor] = useState(getHpBarColor(hpPercentage));

  useMotionValueEvent(steppedHp, 'change', (latest) => {
    const nextColor = getHpBarColor(latest);
    if (nextColor !== currentColor) {
      setCurrentColor(nextColor);
    }
  });

  const width = useTransform(steppedHp, (v) => `${v}%`);

  return (
    <div className="flex flex-row items-center gap-2 flex-1">
      <div className="relative flex-1 h-2.5 bg-hp-bar-bg rounded-sm overflow-hidden shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]">
        <motion.div
          style={{
            width: width,
            backgroundColor: currentColor,
          }}
          className="h-full rounded-sm shadow-[inset_0_-2px_4px_rgba(0,0,0,0.2),inset_0_1px_2px_rgba(255,255,255,0.3)]"
        />
      </div>
    </div>
  );
}

function getHpBarColor(hpPercentage: number): string {
  if (hpPercentage > 50) return 'var(--color-hp-bar-full)';
  if (hpPercentage > 20) return 'var(--color-hp-bar-mid)';
  return 'var(--color-hp-bar-low)';
}
