import { useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';
import { fetchPokemonSprites } from '../api/fetchPokemonSprites';
import type PokemonSprites from '../types/sprites/PokemonSprites';

export default function usePokemonSpritesQuery(names: string[]) {
  const results = useQueries({
    queries: names.map((name) => ({
      queryKey: ['sprites', name],
      queryFn: () => fetchPokemonSprites(name),
      staleTime: 5 * 60 * 1000,
    })),
  });

  const spritesMap = useMemo(() => {
    const map: Record<string, PokemonSprites> = {};
    results.forEach((r, i) => {
      if (r.data) map[names[i]] = r.data;
    });
    return map;
  }, [results, names]);

  const isLoading = results.some((r) => r.isLoading);
  const isError = results.some((r) => r.isError);

  return { spritesMap, isLoading, isError };
}
