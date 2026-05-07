import MiniPokemonSprite from '../pokemon/MiniPokemonSprite';

interface PokemonSwitchProps {
  name: string;
  currentHp: number;
  maxHp: number;
  hpPercentage: number;
  sprite: string;
  onClick: () => void;
  disabled?: boolean;
  types?: string[];
}

export default function PokemonSwitch(props: PokemonSwitchProps) {
  const hpColor =
    props.hpPercentage > 50
      ? '#22c55e'
      : props.hpPercentage > 20
        ? '#eab308'
        : '#ef4444';

  const handleClick = () => {
    if (!props.disabled) {
      props.onClick();
    }
  };

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={props.disabled}
      className={`
        flex bg-card-bg flex-row items-center gap-3 px-3 py-2 rounded-lg border border-[--color-card-border] shadow-sm
        transition-all duration-200
        ${props.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.02] active:scale-[0.98]'}
      `}
    >
      <div className="w-10 h-10 overflow-hidden flex items-center justify-center shrink-0">
        <MiniPokemonSprite
          className="self-center scale-[2]"
          name={props.name}
          sprite={props.sprite}
        />
      </div>
      <div className="flex flex-col gap-1 w-full">
        <span className="text-body font-medium text-[--color-text-primary] leading-none truncate">
          {props.name.charAt(0).toUpperCase() + props.name.slice(1)}
        </span>
        <div className="flex flex-row items-center gap-3 w-full">
          <div className="h-2.5 w-24 bg-[--color-hp-bar-bg] rounded-sm overflow-hidden shadow-[inset_0_2px_4px_rgba(0,0,0,0.3)]">
            <div
              className="h-full rounded-sm shadow-[inset_0_-2px_4px_rgba(0,0,0,0.2),inset_0_1px_2px_rgba(255,255,255,0.3)]"
              style={{
                width: `${props.hpPercentage}%`,
                backgroundColor: hpColor,
              }}
            />
          </div>
          <span className="text-[16px] text-[--color-text-secondary] font-medium leading-none shrink-0">
            {props.currentHp}/{props.maxHp}
          </span>
        </div>
      </div>
    </button>
  );
}
