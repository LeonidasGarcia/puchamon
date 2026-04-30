import HpBar from "../HpBar";

interface PokemonStateProps {
  name: string;
  level: number;
  hpPercentage: number;
  currentHp: number;
  maxHp: number;
}

export default function PokemonState(props: PokemonStateProps) {
  return (
    <div className="flex bg-pokemon-state flex-col gap-0.5 px-3 py-2 rounded-tl-xl rounded-br-xl rounded-tr-xs rounded-bl-xs border-4 border-black min-w-3xs">
      <div className="flex flex-row justify-between gap-4 items-baseline">
        <p className="text-body/[12px]">{props.name}</p>
        <p className="text-small/[28px]">Lv. {props.level}</p>
      </div>
      <div className="flex flex-col gap-2 items-end">
        <HpBar hpPercentage={props.hpPercentage} />
        <p className="text-small/[12px]">
          {props.currentHp}/{props.maxHp}
        </p>
      </div>
    </div>
  );
}
