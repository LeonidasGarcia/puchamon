import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import BattleScenario from '../components/battle/BattleScenario';
import LoadingScreen from '../components/LoadingScreen';
import TurnLog from '../components/battle/TurnLog';
import { useBattleNetworkStore } from '../stores/battleNetworkStore';
import { useGameStore } from '../stores/gameStore';
import { useConnectionStore } from '../stores/connectionStore';
import usePokemonSpritesQuery from '../hooks/usePokemonSpritesQuery';
import PokemonSwitch from '../components/cards/PokemonSwitch';
import Section from '../components/ui/Section';
import Modal from '../components/ui/Modal';
import PokemonState from '../components/cards/PokemonState';
import OpponentTeamPreview from '../components/cards/OpponentTeamPreview';
import PokemonMovement from '../components/cards/PokemonMovement';
import { POKE_DATA } from '../types/Pokemon';
import { AI_DIFFICULTY_LABELS } from '../types/difficulty';
import type { WeatherColorsKeys } from '../types/colors/WeatherColors';
import type { HazardColorsKeys } from '../types/colors/HazardColors';
import type { TypeColorsKeys } from '../types/colors/TypeColors';

export default function App() {
  const { isConnected, lastError, connect, disconnect, sendAction } =
    useBattleNetworkStore();

  const {
    name,
    controllerType,
    difficulty: ai1_difficulty,
    ai2_difficulty,
  } = useConnectionStore();

  const myName =
    controllerType === 'ai'
      ? `${name ?? 'IA 1'} (${AI_DIFFICULTY_LABELS[ai1_difficulty ?? 1]})`
      : (name ?? 'Mi equipo');

  const opponentName =
    AI_DIFFICULTY_LABELS[
      (controllerType === 'ai' ? ai2_difficulty : ai1_difficulty) ?? 1
    ];

  const {
    weather,
    sides,
    myPokemon,
    opponentPokemon,
    trainerId,
    status,
    winnerTrainerId,
    playerPhase,
  } = useGameStore();

  const myActiveInstanceId =
    sides[trainerId ?? '']?.active_pokemon_instance_ids?.[0];
  const activePokemon =
    myPokemon.find((p) => p.instance_id === myActiveInstanceId) ?? myPokemon[0];
  const activeOpponentInstanceId = Object.entries(sides).find(
    ([key]) => key !== trainerId,
  )?.[1]?.active_pokemon_instance_ids?.[0];
  const activeOpponentPokemon = opponentPokemon.find(
    (p) => p.instance_id === activeOpponentInstanceId,
  );

  const opponentTrainerId = Object.keys(sides).find((key) => key !== trainerId);
  const opponentActiveInstanceIds: string[] =
    sides[opponentTrainerId ?? '']?.active_pokemon_instance_ids?.filter(
      (id): id is string => id !== null,
    ) ?? [];
  const opponentTeamPokemon = [...opponentPokemon].sort(
    (a, b) => a.team_slot - b.team_slot,
  );

  const isOpponentFainted =
    activeOpponentPokemon?.fainted &&
    activeOpponentPokemon?.instance_id !== activeOpponentInstanceId;

  const isPlayerFainted =
    activePokemon?.fainted && activePokemon?.instance_id !== myActiveInstanceId;

  const isVictory = winnerTrainerId === trainerId;

  const canAct = playerPhase === 'can_act' || playerPhase === 'awaiting_switch';

  const navigate = useNavigate();

  const handlePlayAgain = () => {
    const { name, controllerType, difficulty, ai2_difficulty, battleType } =
      useConnectionStore.getState();
    if (!name || !difficulty) return;
    disconnect();
    connect({
      name,
      controller_type: controllerType,
      battle_type: battleType,
      difficulty,
      ai2_difficulty: controllerType === 'ai' ? ai2_difficulty : undefined,
    });
  };

  const handleGoToLobby = () => {
    disconnect();
    navigate('/');
  };

  const allTeamBySlot = [...myPokemon].sort(
    (a, b) => a.team_slot - b.team_slot,
  );

  useEffect(() => {
    const { name, controllerType, difficulty, ai2_difficulty, battleType } =
      useConnectionStore.getState();
    if (!name || !difficulty) return;
    connect({
      name,
      controller_type: controllerType,
      battle_type: battleType,
      difficulty,
      ai2_difficulty: controllerType === 'ai' ? ai2_difficulty : undefined,
    });

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const allPokemonIds = [
    ...myPokemon.map((p) => p.pokemon_id),
    ...opponentPokemon.map((p) => p.pokemon_id),
  ];

  const { spritesMap: allSprites, isLoading: spritesLoading } =
    usePokemonSpritesQuery(allPokemonIds);

  const p1Sprites = activePokemon
    ? [allSprites[activePokemon.pokemon_id]].filter(Boolean)
    : [];
  const p2Sprites = activeOpponentPokemon
    ? [allSprites[activeOpponentPokemon.pokemon_id]].filter(Boolean)
    : [];

  const activeMoves = activePokemon?.move_state ?? [];

  const handleMoveSelect = (moveId: string) => {
    if (!activePokemon || !canAct) return;

    sendAction({
      type: 'move',
      user_instance_id: activePokemon.instance_id,
      move_id: moveId,
      target: {
        scope: 'target',
        target_side: 'foe_side',
        target_active_slot: 0,
      },
      replacement_instance_id: null,
    });
  };

  const handleSwitchSelect = (replacementInstanceId: string) => {
    if (!activePokemon) return;

    sendAction({
      type: 'switch',
      user_instance_id: activePokemon.instance_id,
      move_id: null,
      target: null,
      replacement_instance_id: replacementInstanceId,
    });
  };

  const isLoading = !isConnected || spritesLoading;

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (lastError) {
    return (
      <div className="w-screen h-screen flex bg-neutral-900 justify-center items-center">
        <p className="text-red-500 text-body">Error: {lastError.message}</p>
      </div>
    );
  }

  return (
    <div className="w-screen h-screen flex bg-neutral-900 overflow-hidden">
      <div className="flex flex-col gap-4 flex-1 h-full">
        <BattleScenario
          p1Sprites={p1Sprites}
          p2Sprites={p2Sprites}
          weatherId={(weather?.weather_id as WeatherColorsKeys) ?? null}
          weatherRemainingTurns={weather?.remaining_turns ?? null}
          hazards={(sides['p1']?.hazards as HazardColorsKeys[]) ?? []}
          myPokemon={[activePokemon]}
          opponentPokemon={[activeOpponentPokemon]}
          isOpponentFainted={isOpponentFainted}
          isPlayerFainted={isPlayerFainted}
        />
        <div className="flex flex-col gap-6 pb-8">
          <Section label={`Equipo de ${myName}`}>
            {activePokemon && (
              <PokemonState
                key={activePokemon.instance_id}
                name={
                  activePokemon.pokemon_id.charAt(0).toUpperCase() +
                  activePokemon.pokemon_id.slice(1)
                }
                currentHp={activePokemon.current_hp}
                maxHp={activePokemon.max_hp}
                level={activePokemon.level}
                hpPercentage={Math.round(
                  (activePokemon.current_hp / activePokemon.max_hp) * 100,
                )}
                status={activePokemon.status}
              />
            )}
          </Section>
          <Section
            label={`¿Qué debería hacer ${
              activePokemon?.pokemon_id
                ? activePokemon.pokemon_id.charAt(0).toUpperCase() +
                  activePokemon.pokemon_id.slice(1)
                : ''
            }?`}
          >
            {activeMoves.map((move) => {
              const moveData = POKE_DATA.moves.find(
                (m) => m._id === move.move_id,
              );
              const isDisabled = move.current_pp === 0 || !canAct;
              return (
                <PokemonMovement
                  key={move.move_id}
                  name={moveData?.name ?? move.move_id}
                  type={(moveData?.type as TypeColorsKeys) ?? 'Normal'}
                  currentPP={move.current_pp}
                  maxPP={moveData?.pp ?? move.current_pp}
                  disabled={isDisabled}
                  onClick={() => handleMoveSelect(move.move_id)}
                />
              );
            })}
          </Section>
          {
            <Section label="Cambiar Pokemon">
              {allTeamBySlot.map((pokemon) => (
                <PokemonSwitch
                  key={pokemon.instance_id}
                  name={pokemon.pokemon_id}
                  currentHp={pokemon.current_hp}
                  maxHp={pokemon.max_hp}
                  hpPercentage={Math.round(
                    (pokemon.current_hp / pokemon.max_hp) * 100,
                  )}
                  sprite={allSprites[pokemon.pokemon_id]?.minisprite}
                  onClick={() => handleSwitchSelect(pokemon.instance_id)}
                  disabled={
                    pokemon.fainted ||
                    pokemon.instance_id === myActiveInstanceId ||
                    !canAct
                  }
                />
              ))}
            </Section>
          }
        </div>
      </div>
      <div className="flex flex-col gap-8 flex-1 py-6 h-full">
        <div className="flex flex-col gap-6">
          <Section
            label={`Equipo de IA (${opponentName})`}
            className="flex-col items-center"
          >
            {activeOpponentPokemon && (
              <PokemonState
                key={activeOpponentPokemon.instance_id}
                name={
                  activeOpponentPokemon.pokemon_id.charAt(0).toUpperCase() +
                  activeOpponentPokemon.pokemon_id.slice(1)
                }
                currentHp={activeOpponentPokemon.current_hp}
                maxHp={activeOpponentPokemon.max_hp}
                level={activeOpponentPokemon.level}
                hpPercentage={Math.round(
                  (activeOpponentPokemon.current_hp /
                    activeOpponentPokemon.max_hp) *
                    100,
                )}
                status={activeOpponentPokemon.status}
              />
            )}
            <OpponentTeamPreview
              pokemon={opponentTeamPokemon}
              activeInstanceIds={opponentActiveInstanceIds}
              spritesMap={allSprites}
            />
          </Section>
        </div>
        <Section
          className="flex flex-col items-start justify-start overflow-scroll"
          label="Turnos"
        >
          <TurnLog />
        </Section>
        {status === 'finished' && playerPhase === 'finished' && (
          <Modal isOpen>
            <h2 className="text-2xl font-bold text-white mb-4 text-center">
              {isVictory ? '¡Victoria!' : 'Derrota'}
            </h2>
            <div className="flex gap-4 justify-center">
              <button
                onClick={handlePlayAgain}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Volver a Jugar
              </button>
              <button
                onClick={handleGoToLobby}
                className="px-4 py-2 bg-neutral-600 text-white rounded-lg hover:bg-neutral-700"
              >
                Ir al Inicio
              </button>
            </div>
          </Modal>
        )}
      </div>
    </div>
  );
}
