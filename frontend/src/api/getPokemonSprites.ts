import type PokemonSprites from "../types/PokemonSprites";
import {
  miniPokeSpritesAxiosInstance,
  pokeSpritesAxiosInstance,
} from "./axiosInstance";

export default async function getPokemonSprites(
  name: string,
): Promise<PokemonSprites> {
  const normalResponse = await pokeSpritesAxiosInstance.get(
    "/normal/" + name + ".gif",
    {
      responseType: "blob",
    },
  );
  const backResponse = await pokeSpritesAxiosInstance.get(
    "/back-normal/" + name + ".gif",
    {
      responseType: "blob",
    },
  );

  const miniSprite = await miniPokeSpritesAxiosInstance.get(name + ".png", {
    responseType: "blob",
  });

  const miniSpriteUrl = URL.createObjectURL(miniSprite.data);

  const normalBlob = normalResponse.data;
  const backBlob = backResponse.data;

  const normalUrl = URL.createObjectURL(normalBlob);
  const backUrl = URL.createObjectURL(backBlob);

  return {
    normal: normalUrl,
    back_normal: backUrl,
    minisprite: miniSpriteUrl,
  };
}
