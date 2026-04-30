import axios from "axios";

// normal y back-normal
export const pokeSpritesAxiosInstance = axios.create({
  baseURL: "/poke-gifs/sprites/black-white/anim",
});

export const miniPokeSpritesAxiosInstance = axios.create({
  baseURL: "/mini-poke-sprites/msikma/pokesprite/master/pokemon-gen7x/regular/",
});
