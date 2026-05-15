import { getTypeColor, type TypeColorsKeys } from '../../types/colors/TypeColors';

interface PokemonMovementProps {
  name: string;
  type: TypeColorsKeys;
  currentPP: number;
  maxPP: number;
  onClick: () => void;
  disabled?: boolean;
}

function blendWithWhite(hex: string, intensity: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  const whiteR = 255;
  const whiteG = 255;
  const whiteB = 255;
  const blendedR = Math.round(whiteR + (r - whiteR) * intensity);
  const blendedG = Math.round(whiteG + (g - whiteG) * intensity);
  const blendedB = Math.round(whiteB + (b - whiteB) * intensity);
  return `rgb(${blendedR}, ${blendedG}, ${blendedB})`;
}

export default function PokemonMovement(props: PokemonMovementProps) {
  const typeColor = getTypeColor(props.type);
  const backgroundColor = blendWithWhite(typeColor, 0.25);

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
        flex flex-row items-center justify-between px-3 py-2 rounded-lg border-2 min-w-52 shadow-sm
        transition-opacity duration-200
        ${props.disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.02] active:scale-[0.98]'}
      `}
      style={{ backgroundColor, borderColor: typeColor }}
    >
      <div className="flex flex-col gap-0.5">
        <span className="text-body font-medium text-[--color-text-primary] leading-none">
          {props.name}
        </span>
        <span
          className="text-movement-type font-medium leading-none"
          style={{ color: typeColor }}
        >
          {props.type}
        </span>
      </div>
      <span className="text-movement-type text-[--color-text-secondary] font-medium leading-none shrink-0">
        {props.currentPP}/{props.maxPP}
      </span>
    </button>
  );
}