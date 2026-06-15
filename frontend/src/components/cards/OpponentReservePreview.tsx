import MiniPokemonSprite from '../pokemon/MiniPokemonSprite';
import type PokemonSprites from '../../types/sprites/PokemonSprites';
import type { PokemonInstanceSnapshot } from '../../types/schemas/Battle';

interface OpponentReservePreviewProps {
  pokemon: PokemonInstanceSnapshot[];
  spritesMap: Record<string, PokemonSprites>;
}

function UnknownPokemonSlot() {
  return <span className="text-text-secondary text-body font-bold">?</span>;
}

export default function OpponentReservePreview({
  pokemon,
  spritesMap,
}: OpponentReservePreviewProps) {
  if (pokemon.length === 0) return null;

  return (
    <div className="flex gap-2 mt-1 justify-center">
      {pokemon.map((p) => (
        <div
          key={p.instance_id}
          className={`flex items-center justify-center w-16 h-16 rounded-lg ${
            p.fainted ? 'opacity-40 grayscale' : ''
          }`}
        >
          {p.is_revealed ? (
            <MiniPokemonSprite
              rescalingConstant={1.2}
              name={p.pokemon_id}
              sprite={spritesMap[p.pokemon_id]?.minisprite}
            />
          ) : (
            <UnknownPokemonSlot />
          )}
        </div>
      ))}
    </div>
  );
}
