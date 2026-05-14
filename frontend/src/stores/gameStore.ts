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
    const { animationQueue } = get();
    const newQueue = [...animationQueue, turn];

    if (animationQueue.length === 0) {
      set({
        animationQueue: newQueue,
        currentTurn: turn,
        currentEventIndex: 0,
        playerPhase: 'animating',
      });
    } else {
      set({ animationQueue: newQueue });
    }
  },

  onEventComplete: () => {
    const { currentTurn, currentEventIndex, animationQueue, trainerId } = get();
    const events = currentTurn?.events ?? [];
    const nextEventIndex = currentEventIndex + 1;

    if (nextEventIndex >= events.length) {
      const remainingQueue = animationQueue.slice(1);

      if (remainingQueue.length > 0) {
        const nextTurn = remainingQueue[0];
        set({
          animationQueue: remainingQueue,
          currentTurn: nextTurn,
          currentEventIndex: 0,
        });
      } else {
        const committedTurn = currentTurn;
        if (!committedTurn) return;

        const snapshot = committedTurn.post_turn_snapshot;
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
          turnHistory: [...get().turnHistory, committedTurn],
          status: snapshot.status,
          winnerTrainerId: snapshot.result?.winner_trainer_id ?? null,
        });

        get().calculateNextPhase();
      }
    } else {
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