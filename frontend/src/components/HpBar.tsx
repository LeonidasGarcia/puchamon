import {
  motion,
  useMotionValue,
  useSpring,
  useTransform,
  useMotionValueEvent,
} from "framer-motion";
import { useEffect, useState } from "react";

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

  useMotionValueEvent(steppedHp, "change", (latest) => {
    const nextColor = getHpBarColor(latest);
    if (nextColor !== currentColor) {
      setCurrentColor(nextColor);
    }
  });

  const width = useTransform(steppedHp, (v) => `${v}%`);

  return (
    <div className="flex flex-row min-w-32 h-3.5 p-0.5 pl-1.5 bg-black gap-1 items-center rounded-full">
      <p className="text-[10px] font-bold text-hp-bar-label leading-none">HP</p>
      <div className="flex-1 h-full rounded-full bg-white overflow-hidden border border-black">
        <motion.div
          style={{
            width: width,
            backgroundColor: currentColor,
          }}
          className="h-full rounded-full"
        />
      </div>
    </div>
  );
}

function getHpBarColor(hpPercentage: number): string {
  if (hpPercentage > 50) return "#4ade80";
  if (hpPercentage > 20) return "#facc15";
  return "#ef4444";
}
