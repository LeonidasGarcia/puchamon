interface StatusBadgeProps {
  status: string | null | undefined;
}

const STATUS_MAP: Record<string, { label: string; className: string }> = {
  burn: { label: 'BRN', className: 'bg-orange-600 text-white' },
  burned: { label: 'BRN', className: 'bg-orange-600 text-white' },
  brn: { label: 'BRN', className: 'bg-orange-600 text-white' },
  paralysis: { label: 'PAR', className: 'bg-yellow-400 text-black' },
  paralyzed: { label: 'PAR', className: 'bg-yellow-400 text-black' },
  par: { label: 'PAR', className: 'bg-yellow-400 text-black' },
  poison: { label: 'PSN', className: 'bg-purple-600 text-white' },
  poisoned: { label: 'PSN', className: 'bg-purple-600 text-white' },
  psn: { label: 'PSN', className: 'bg-purple-600 text-white' },
  toxic: { label: 'TOX', className: 'bg-purple-800 text-white' },
  bad_poison: { label: 'TOX', className: 'bg-purple-800 text-white' },
  badly_poisoned: { label: 'TOX', className: 'bg-purple-800 text-white' },
  tox: { label: 'TOX', className: 'bg-purple-800 text-white' },
  sleep: { label: 'SLP', className: 'bg-slate-400 text-white' },
  asleep: { label: 'SLP', className: 'bg-slate-400 text-white' },
  slp: { label: 'SLP', className: 'bg-slate-400 text-white' },
  freeze: { label: 'FRZ', className: 'bg-cyan-400 text-black' },
  frozen: { label: 'FRZ', className: 'bg-cyan-400 text-black' },
  frz: { label: 'FRZ', className: 'bg-cyan-400 text-black' },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  if (!status) return null;

  const entry = STATUS_MAP[status.toLowerCase()];
  if (!entry) return null;

  return (
    <span
      className={`inline-flex items-center justify-center px-1.5 py-0.5 rounded text-[10px] font-bold leading-none tracking-wide ${entry.className}`}
    >
      {entry.label}
    </span>
  );
}
