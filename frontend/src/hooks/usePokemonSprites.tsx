import { useEffect, useState } from "react";
import type PokemonSprites from "../types/PokemonSprites";
import getPokemonSprites from "../api/getPokemonSprites";

type PokemonSetSprites = {
  [K in string]: PokemonSprites;
};

export default function usePokemonSprites(names: string[]) {
  const [sprites, setSprites] = useState<PokemonSetSprites | undefined>(
    undefined,
  );

  useEffect(() => {
    (async () => {
      for (let name of names) {
        const newSprites = await getPokemonSprites(name);

        console.log(sprites);

        setSprites((prev) => ({
          ...prev,
          [name]: newSprites,
        }));
      }
    })();
  }, []);

  return sprites;
}
