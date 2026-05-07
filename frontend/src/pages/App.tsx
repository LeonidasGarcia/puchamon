import BattleScenario from '../components/battle/BattleScenario';
import LoadingScreen from '../components/LoadingScreen';
import TurnLog from '../components/battle/TurnLog';
import { POKE_DATA } from '../types/Pokemon';
import { SAMPLE_TURNS } from '../data/sampleTurns';
import usePokemonSpritesQuery from '../hooks/usePokemonSpritesQuery';
import PokemonSwitch from '../components/cards/PokemonSwitch';
import Section from '../components/ui/Section';
import PokemonState from '../components/cards/PokemonState';
import PokemonMovement from '../components/cards/PokemonMovement';

const p1Pokemons = shufflePokemons();
const p2Pokemons = shufflePokemons();

const p1PokemonsMovesets = p1Pokemons.map((pokemon) =>
  pickPokemonMoveset(pokemon._id),
);
const p2PokemonsMovesets = p2Pokemons.map((pokemon) =>
  pickPokemonMoveset(pokemon._id),
);

const p1PokemonMoves = {};
const p2PokemonMoves = {};

p1PokemonsMovesets.forEach((set) => {
  p1PokemonMoves[set.pokemonId] = set.moves.map((move) =>
    POKE_DATA.moves.find((savedMove) => savedMove._id === move),
  );
});

p2PokemonsMovesets.forEach((set) => {
  p2PokemonMoves[set.pokemonId] = set.moves.map((move) =>
    POKE_DATA.moves.find((savedMove) => savedMove._id === move),
  );
});

const trainers = {
  p1: {
    name: 'Leo',
    pokemons: p1Pokemons,
    pokemonsMovesets: p1PokemonsMovesets,
    pokemonMoves: p1PokemonMoves,
  },
  p2: {
    name: 'Nick',
    pokemons: p2Pokemons,
    pokemonsMovesets: p2PokemonsMovesets,
    pokemonMoves: p2PokemonMoves,
  },
};

export default function App() {
  const { spritesMap: p1Sprites, isLoading: p1Loading } =
    usePokemonSpritesQuery(trainers.p1.pokemons.map((poke) => poke._id));
  const { spritesMap: p2Sprites, isLoading: p2Loading } =
    usePokemonSpritesQuery(trainers.p2.pokemons.map((poke) => poke._id));

  const areSpritesLoading = p1Loading || p2Loading;

  return (
    <>
      {areSpritesLoading ? (
        <LoadingScreen />
      ) : (
        <div className="w-screen h-screen flex bg-neutral-900 overflow-hidden">
          <div className="flex flex-col gap-4 flex-1 h-full">
            <BattleScenario
              p1Sprites={Object.values(p1Sprites)
                .slice(0, 3)
                .map((sprite) => sprite)}
              p2Sprites={Object.values(p2Sprites)
                .slice(0, 3)
                .map((sprite) => sprite)}
              weatherId="hail"
              weatherRemainingTurns={3}
              hazards={['spikes', 'stealth-rock']}
            />
            <div className="flex flex-col gap-6 pb-8">
              <Section label="Leo">
                {trainers.p1.pokemons.slice(0, 3).map((pokemon) => (
                  <PokemonState
                    name={pokemon.name}
                    currentHp={pokemon.baseStats.hp}
                    maxHp={pokemon.baseStats.hp}
                    level={100}
                    hpPercentage={100}
                  />
                ))}
              </Section>
              <Section label="¿Qué debería hacer Pikachu?">
                {trainers.p1.pokemonMoves[trainers.p1.pokemons[0]._id].map(
                  (move) => (
                    <PokemonMovement
                      name={move.name}
                      type={move.type}
                      currentPP={move.pp}
                      maxPP={move.pp}
                    />
                  ),
                )}
              </Section>
              <Section label="Cambiar Pokemon">
                <PokemonSwitch
                  name={p1Pokemons[3].name}
                  currentHp={Math.round(p1Pokemons[3].baseStats.hp * 0.35)}
                  maxHp={p1Pokemons[3].baseStats.hp}
                  hpPercentage={35}
                  sprite={p1Sprites[p1Pokemons[3]._id]?.minisprite}
                />
                <PokemonSwitch
                  name={p1Pokemons[4].name}
                  currentHp={Math.round(p1Pokemons[4].baseStats.hp * 0.35)}
                  maxHp={p1Pokemons[4].baseStats.hp}
                  hpPercentage={35}
                  sprite={p1Sprites[p1Pokemons[4]._id]?.minisprite}
                />
                <PokemonSwitch
                  name={p1Pokemons[5].name}
                  currentHp={Math.round(p1Pokemons[5].baseStats.hp * 0.35)}
                  maxHp={p1Pokemons[5].baseStats.hp}
                  hpPercentage={35}
                  sprite={p1Sprites[p1Pokemons[5]._id]?.minisprite}
                />
              </Section>
            </div>
          </div>
          <div className="flex flex-col gap-8 flex-1 py-6 h-full">
            <div className="flex flex-col gap-6">
              <Section label="Trainer Nick">
                <PokemonState
                  name="Pikachu"
                  currentHp={100}
                  maxHp={145}
                  level={50}
                  hpPercentage={90}
                />
                <PokemonState
                  name="Pikachu"
                  currentHp={100}
                  maxHp={145}
                  level={50}
                  hpPercentage={90}
                />
                <PokemonState
                  name="Pikachu"
                  currentHp={100}
                  maxHp={145}
                  level={50}
                  hpPercentage={90}
                />
              </Section>
            </div>
            <Section
              className="flex flex-col items-start justify-start overflow-scroll"
              label="Turnos"
            >
              <TurnLog turns={SAMPLE_TURNS} />
            </Section>
          </div>
        </div>
      )}
    </>
  );
}

function shufflePokemons() {
  return [...POKE_DATA.pokemons].sort(() => 0.5 - Math.random()).slice(0, 6);
}

function pickPokemonMoveset(pokemonId: string) {
  return [...POKE_DATA.movesets]
    .filter((set) => set.pokemonId == pokemonId)
    .sort(() => 0.5 - Math.random())[0];
}
