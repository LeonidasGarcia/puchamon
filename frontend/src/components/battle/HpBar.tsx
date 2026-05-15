import { motion } from 'framer-motion';
import type { FC } from 'react';

interface HpBarProps {
  hpPercentage: number;
}

const HpBar: FC<HpBarProps> = ({ hpPercentage }) => {
  const currentColor =
    hpPercentage > 50
      ? 'var(--color-hp-bar-full)'
      : hpPercentage > 20
        ? 'var(--color-hp-bar-mid)'
        : 'var(--color-hp-bar-low)';

  return (
    <div className="flex flex-row items-center gap-2 flex-1">
      <div className="relative flex-1 h-2.5 bg-hp-bar-bg rounded-sm overflow-hidden shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]">
        <motion.div
          initial={{ width: `${hpPercentage}%` }}
          animate={{ width: `${hpPercentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          style={{
            backgroundColor: currentColor,
          }}
          className="h-full rounded-sm shadow-[inset_0_-2px_4px_rgba(0,0,0,0.2),inset_0_1px_2px_rgba(255,255,255,0.3)]"
        />
      </div>
    </div>
  );
};

export default HpBar;
