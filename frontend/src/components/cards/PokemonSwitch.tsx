import HpBar from "../HpBar";
import MiniPokemonSprite from "../MiniPokemonSprite";

interface PokemonSwitchProps {
  name: string;
  hpPercentage: number;
  sprite: string;
}

export default function PokemonSwitch(props: PokemonSwitchProps) {
  return (
    <div className="flex bg-pokemon-state flex-row pr-3 py-2 rounded-sm border-3 border-black">
      <MiniPokemonSprite
        className="self-end"
        name={props.name}
        sprite={props.sprite}
      />
      <div className="flex flex-col gap-1">
        <p className="text-small/[24px]">{props.name}</p>
        <HpBar hpPercentage={props.hpPercentage} />
      </div>
    </div>
  );
}
