import Ground from "./Ground";
import PokemonSprite from "./PokemonSprite";
import type PokemonSprites from "../types/PokemonSprites";

interface BattleScenarioProps {
  p1Sprites: PokemonSprites[];
  p2Sprites: PokemonSprites[];
}

export default function BattleScenario(props: BattleScenarioProps) {
  return (
    <div className="w-240 h-135 p-8 rounded-br-3xl bg-[#DBDBBE] grid grid-rows-2 grid-cols-2">
      <div></div>
      <div className="relative flex w-64 h-16 flex-start self-end items-end justify-center py-4">
        {props.p2Sprites.map((sprite) => (
          <PokemonSprite sprite={sprite?.normal} />
        ))}
        <Ground className="absolute z-0 top-1" />
      </div>
      <div className="relative flex w-64 h-16 flex-start self-end justify-self-end items-end justify-center py-6">
        {props.p1Sprites.map((sprite) => (
          <PokemonSprite sprite={sprite?.back_normal} />
        ))}
        <Ground className="absolute z-0 top-0.5" />
      </div>
      <div></div>
    </div>
  );
}
