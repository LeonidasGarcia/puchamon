import HpBar from '../battle/HpBar';

interface PokemonStateProps {
  name: string;
  level: number;
  hpPercentage: number;
  currentHp: number;
  maxHp: number;
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
          {props.currentHp}/{props.maxHp}
        </span>
      </div>
    </div>
  );
}
