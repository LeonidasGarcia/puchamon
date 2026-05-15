import { create } from 'zustand';
import type {
  BattleTurnDTO,
  BattleSnapshot,
  PokemonInstanceSnapshot,
  Player,
} from '../types/schemas/Battle';

export type PlayerPhase =
  | 'can_act'
  | 'animating'
  | 'awaiting_switch'
  | 'spectating'
  | 'finished';

interface InitializeData {
  controllerType: 'human' | 'ai';
  trainerId: string;
  myPokemon: PokemonInstanceSnapshot[];
  opponentPokemon: PokemonInstanceSnapshot[];
  weather: BattleSnapshot['weather'];
  sides: BattleSnapshot['sides'];
  status: 'active' | 'finished' | 'paused' | null;
  players: Player[];
}

interface GameState {
  animationQueue: BattleTurnDTO[];
  currentTurn: BattleTurnDTO | null;
  currentEventIndex: number;
  myPokemon: PokemonInstanceSnapshot[];
  opponentPokemon: PokemonInstanceSnapshot[];
  weather: BattleSnapshot['weather'];
  sides: BattleSnapshot['sides'];
  turnHistory: BattleTurnDTO[];
  playerPhase: PlayerPhase;
  controllerType: 'human' | 'ai';
  trainerId: string | null;
  status: 'active' | 'finished' | 'paused' | null;
  winnerTrainerId: string | null;
  availableSwitches: string[];
}

interface GameActions {
  initialize: (data: InitializeData) => void;
  reset: () => void;
  enqueueTurn: (turn: BattleTurnDTO) => void;
  onEventComplete: () => void;
  calculateNextPhase: () => void;
}

type GameStore = GameState & GameActions;

export const useGameStore = create<GameStore>((set, get) => ({
  animationQueue: [],
  currentTurn: null,
  currentEventIndex: 0,
  myPokemon: [],
  opponentPokemon: [],
  weather: null,
  sides: {},
  turnHistory: [],
  playerPhase: 'spectating',
  controllerType: 'ai',
  trainerId: null,
  status: null,
  winnerTrainerId: null,
  availableSwitches: [],

  initialize: (data: InitializeData) => {
    const initialPhase =
      data.controllerType === 'ai' ? 'spectating' : 'can_act';

    set({
      controllerType: data.controllerType,
      trainerId: data.trainerId,
      myPokemon: data.myPokemon,
      opponentPokemon: data.opponentPokemon,
      weather: data.weather,
      sides: data.sides,
      status: data.status,
      playerPhase: initialPhase,
      animationQueue: [],
      currentTurn: null,
      currentEventIndex: 0,
      turnHistory: [],
      winnerTrainerId: null,
      availableSwitches: [],
    });
  },

  reset: () => {
    set({
      animationQueue: [],
      currentTurn: null,
      currentEventIndex: 0,
      myPokemon: [],
      opponentPokemon: [],
      weather: null,
      sides: {},
      turnHistory: [],
      playerPhase: 'spectating',
      controllerType: 'ai',
      trainerId: null,
      status: null,
      winnerTrainerId: null,
      availableSwitches: [],
    });
  },

  enqueueTurn: (turn: BattleTurnDTO) => {
    const { animationQueue, trainerId } = get();
    const newQueue = [...animationQueue, turn];

    if (animationQueue.length === 0) {
      const snapshot = turn.post_turn_snapshot;
      const newMyPokemon = snapshot.pokemon_instances.filter(
        (p: PokemonInstanceSnapshot) => p.trainer_id === trainerId,
      );
      const newOpponentPokemon = snapshot.pokemon_instances.filter(
        (p: PokemonInstanceSnapshot) => p.trainer_id !== trainerId,
      );

      set({
        animationQueue: [],
        currentTurn: null,
        currentEventIndex: 0,
        myPokemon: newMyPokemon,
        opponentPokemon: newOpponentPokemon,
        weather: snapshot.weather,
        sides: snapshot.sides,
        turnHistory: [...get().turnHistory, turn],
        status: snapshot.status,
        winnerTrainerId: snapshot.result?.winner_trainer_id ?? null,
      });

      get().calculateNextPhase();
    } else {
      set({ animationQueue: newQueue });
    }
  },

  onEventComplete: () => {
    const { currentTurn, currentEventIndex, animationQueue, trainerId } = get();
    const events = currentTurn?.events ?? [];
    const nextEventIndex = currentEventIndex + 1;

    console.log('[gameStore] onEventComplete called', {
      currentEventIndex,
      nextEventIndex,
      eventsLength: events.length,
      animationQueueLength: animationQueue.length,
    });

    if (nextEventIndex >= events.length) {
      const remainingQueue = animationQueue.slice(1);

      console.log('[gameStore] Last event of turn', {
        remainingQueueLength: remainingQueue.length,
      });

      if (remainingQueue.length > 0) {
        const nextTurn = remainingQueue[0];
        console.log(
          '[gameStore] Processing next turn from queue:',
          nextTurn.turn,
        );
        set({
          animationQueue: remainingQueue,
          currentTurn: nextTurn,
          currentEventIndex: 0,
        });
      } else {
        const committedTurn = currentTurn;
        if (!committedTurn) {
          console.log('[gameStore] committedTurn is null, returning early');
          return;
        }

        console.log(
          '[gameStore] All events complete, committing turn',
          committedTurn.turn,
        );
        const snapshot = committedTurn.post_turn_snapshot;
        const newMyPokemon = snapshot.pokemon_instances.filter(
          (p: PokemonInstanceSnapshot) => p.trainer_id === trainerId,
        );
        const newOpponentPokemon = snapshot.pokemon_instances.filter(
          (p: PokemonInstanceSnapshot) => p.trainer_id !== trainerId,
        );

        console.log('[gameStore] Updating turnHistory');

        set({
          animationQueue: [],
          currentTurn: null,
          currentEventIndex: 0,
          myPokemon: newMyPokemon,
          opponentPokemon: newOpponentPokemon,
          weather: snapshot.weather,
          sides: snapshot.sides,
          turnHistory: [...get().turnHistory, committedTurn],
          status: snapshot.status,
          winnerTrainerId: snapshot.result?.winner_trainer_id ?? null,
        });

        console.log(
          '[gameStore] turnHistory updated, new length:',
          get().turnHistory.length,
        );

        get().calculateNextPhase();
      }
    } else {
      console.log('[gameStore] Advancing to next event:', nextEventIndex);
      set({ currentEventIndex: nextEventIndex });
    }
  },

  calculateNextPhase: () => {
    const { status, controllerType, currentTurn, trainerId } = get();

    if (status === 'finished') {
      set({ playerPhase: 'finished' });
      return;
    }

    if (controllerType === 'ai') {
      set({ playerPhase: 'spectating' });
      return;
    }

    const requiredReplacements = currentTurn?.required_replacements ?? [];
    const myReplacements = requiredReplacements.find(
      (r: { trainer_id: string; available_instance_ids: string[] }) =>
        r.trainer_id === trainerId,
    );

    if (myReplacements && myReplacements.available_instance_ids.length > 0) {
      set({
        playerPhase: 'awaiting_switch',
        availableSwitches: myReplacements.available_instance_ids,
      });
    } else {
      set({ playerPhase: 'can_act', availableSwitches: [] });
    }
  },
}));
