import { useEffect, useRef } from 'react';
import BattleScenario from '../components/battle/BattleScenario';
import LoadingScreen from '../components/LoadingScreen';
import TurnLog from '../components/battle/TurnLog';
import { useBattleStore } from '../stores/battleStore';
import usePokemonSpritesQuery from '../hooks/usePokemonSpritesQuery';
import PokemonSwitch from '../components/cards/PokemonSwitch';
import Section from '../components/ui/Section';
import Modal from '../components/ui/Modal';
import PokemonState from '../components/cards/PokemonState';
import PokemonMovement from '../components/cards/PokemonMovement';
import { POKE_DATA } from '../types/Pokemon';
import type { WeatherColorsKeys } from '../types/colors/WeatherColors';
import type { HazardColorsKeys } from '../types/colors/HazardColors';
import type { TypeColorsKeys } from '../types/colors/TypeColors';

export default function App() {
  const {
    isConnected,
    isMyTurn,
    isAnimating,
    currentEventIndex,
    currentEvents,
    lastError,
    weather,
    sides,
    players,
    myPokemon,
    opponentPokemon,
    pendingMyPokemon,
    pendingOpponentPokemon,
    turnHistory,
    trainerId,
    status,
    winnerTrainerId,
    connect,
    disconnect,
    submitAction,
    _advanceAnimation,
  } = useBattleStore();

  const myName =
    players.find((p) => p.controller_type === 'human')?.name ?? 'Mi equipo';
  const opponentName =
    players.find((p) => p.controller_type === 'ai')?.name ?? 'Equipo rival';

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

  const displayedOpponentPokemon = isAnimating
    ? (activeOpponentPokemon ?? pendingOpponentPokemon?.find((p) => p.fainted))
    : (activeOpponentPokemon ?? opponentPokemon.find((p) => p.fainted));

  const displayedPlayerPokemon = isAnimating
    ? (activePokemon ?? pendingMyPokemon?.find((p) => p.fainted))
    : (activePokemon ?? myPokemon.find((p) => p.fainted));

  const isOpponentFainted =
    displayedOpponentPokemon?.fainted &&
    displayedOpponentPokemon?.instance_id !== activeOpponentInstanceId;

  const isPlayerFainted =
    displayedPlayerPokemon?.fainted &&
    displayedPlayerPokemon?.instance_id !== myActiveInstanceId;

  const isVictory = winnerTrainerId === trainerId;

  const handlePlayAgain = () => {
    disconnect();
    connect({
      name: 'Leo',
      controller_type: 'human',
      battle_type: '1v1',
      difficulty: 1,
    });
  };

  const allTeamBySlot = [...myPokemon].sort(
    (a, b) => a.team_slot - b.team_slot,
  );

  const displayedTeamPokemon = (() => {
    if (isAnimating && pendingMyPokemon) {
      return [...pendingMyPokemon].sort((a, b) => a.team_slot - b.team_slot);
    }
    return allTeamBySlot;
  })();

  const animationTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (isAnimating && currentEvents.length > 0) {
      animationTimerRef.current = setInterval(() => {
        _advanceAnimation();
      }, 1000);
    }

    return () => {
      if (animationTimerRef.current) {
        clearInterval(animationTimerRef.current);
        animationTimerRef.current = null;
      }
    };
  }, [isAnimating, currentEvents.length, _advanceAnimation]);

  useEffect(() => {
    connect({
      name: 'Leo',
      controller_type: 'human',
      battle_type: '1v1',
      difficulty: 2,
    });

    return () => {
      if (animationTimerRef.current) {
        clearInterval(animationTimerRef.current);
      }
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
  const p2Sprites = displayedOpponentPokemon
    ? [allSprites[displayedOpponentPokemon.pokemon_id]].filter(Boolean)
    : [];

  const activeMoves = activePokemon?.move_state ?? [];

  const handleMoveSelect = (moveId: string) => {
    if (!activePokemon || !isMyTurn || isAnimating) return;

    submitAction({
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
    if (!activePokemon || isAnimating) return;

    submitAction({
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
          isAnimating={isAnimating}
          currentEventIndex={currentEventIndex}
          currentEvents={currentEvents}
          myPokemon={myPokemon}
          opponentPokemon={opponentPokemon}
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
              const isDisabled = move.current_pp === 0 || isAnimating;
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
              {displayedTeamPokemon.map((pokemon) => (
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
                    isAnimating
                  }
                />
              ))}
            </Section>
          }
        </div>
      </div>
      <div className="flex flex-col gap-8 flex-1 py-6 h-full">
        <div className="flex flex-col gap-6">
          <Section label={`Equipo de ${opponentName}`}>
            {displayedOpponentPokemon && (
              <PokemonState
                key={displayedOpponentPokemon.instance_id}
                name={
                  displayedOpponentPokemon.pokemon_id.charAt(0).toUpperCase() +
                  displayedOpponentPokemon.pokemon_id.slice(1)
                }
                currentHp={displayedOpponentPokemon.current_hp}
                maxHp={displayedOpponentPokemon.max_hp}
                level={displayedOpponentPokemon.level}
                hpPercentage={Math.round(
                  (displayedOpponentPokemon.current_hp /
                    displayedOpponentPokemon.max_hp) *
                    100,
                )}
              />
            )}
          </Section>
        </div>
        <Section
          className="flex flex-col items-start justify-start overflow-scroll"
          label="Turnos"
        >
          <TurnLog
            turns={turnHistory}
            isAnimating={isAnimating}
            currentEventIndex={currentEventIndex}
          />
        </Section>
        {status === 'finished' && !isAnimating && currentEvents.length === 0 && (
          <Modal isOpen>
            <h2 className="text-2xl font-bold text-white mb-4">
              {isVictory ? '¡Victoria!' : 'Derrota'}
            </h2>
            <button
              onClick={handlePlayAgain}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Jugar de Nuevo
            </button>
          </Modal>
        )}
      </div>
    </div>
  );
}
