import { create } from 'zustand';
import type {
  BattleTurnDTO,
  BattleSnapshot,
  BattleTurnEvent,
  PokemonInstanceSnapshot,
  Player,
} from '../types/schemas/Battle';

/**
 * PlayerPhase represents the current phase/state of the human player in the battle.
 * - can_act: Player has an active turn available to declare an action.
 * - awaiting_switch: Player must perform a mandatory switch (e.g., after a faint).
 * - spectating: Player is watching an AI vs AI battle, cannot act.
 * - finished: Battle has ended.
 * - animating: Animation system is processing events, player cannot act.
 */
export type PlayerPhase =
  | 'can_act'
  | 'awaiting_switch'
  | 'spectating'
  | 'finished'
  | 'animating';

/**
 * InitializeData is the payload received from the server via `connection:response`.
 * It contains all the initial state needed to set up the battle client-side.
 */
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

/**
 * GameState holds all the centralized game state for the battle UI.
 * This is the single source of truth for what the player sees.
 *
 * Key relationships:
 * - `sides[trainerId].active_pokemon_instance_ids` points to the active slot(s).
 * - `myPokemon` / `opponentPokemon` are derived from `pokemon_instances` filtered by trainer_id.
 * - `turnHistory` contains the turn being animated (last element) and any turns that have
 *   completed animation in sequence mode. In burst mode (AI vs AI), also accumulates pending turns.
 * - `turnQueue` holds pending turns that arrived while a turn was still being animated.
 *   In sequence mode (Human vs AI), this queue is empty because turns arrive one at a time
 *   after player action.
 */
interface GameState {
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

  /** Queue of turns that arrived while a turn was still being animated (AI vs AI bursts). */
  turnQueue: BattleTurnDTO[];
}

/**
 * GameActions contains all mutations to the game state.
 * All state changes flow through these explicit actions.
 */
interface GameActions {
  initialize: (data: InitializeData) => void;
  reset: () => void;

  addTurn: (turn: BattleTurnDTO) => void;

  applyEventKind: (event: BattleTurnEvent) => void;

  finalizeTurnAnimation: () => void;
}

type GameStore = GameState & GameActions;

export const useGameStore = create<GameStore>((set, get) => ({
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

  turnQueue: [],

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
      turnHistory: [],
      winnerTrainerId: null,
      availableSwitches: [],
      turnQueue: [],
    });
  },

  reset: () => {
    set({
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
      turnQueue: [],
    });
  },

  addTurn: (turn: BattleTurnDTO) => {
    const { turnHistory, turnQueue, playerPhase } = get();

    if (
      turnHistory.length === 0 ||
      (turnQueue.length === 0 &&
        (playerPhase === 'can_act' || playerPhase === 'awaiting_switch'))
    ) {
      set({ turnHistory: [...turnHistory, turn], playerPhase: 'animating' });
    } else {
      set((state) => ({
        turnQueue: [...state.turnQueue, turn],
        playerPhase: 'animating',
      }));
    }
  },

  applyEventKind: (event: BattleTurnEvent) => {
    const { turnHistory } = get();
    const currentTurn = turnHistory[turnHistory.length - 1];
    if (!currentTurn) return;

    const snapshot = currentTurn.post_turn_snapshot;
    const targetId = event.target_instance_id;

    switch (event.kind) {
      case 'damage':
      case 'condition_damage':
      case 'heal_hp': {
        if (targetId) {
          const target = snapshot.pokemon_instances.find(
            (p) => p.instance_id === targetId,
          );
          if (target) {
            set((state) => ({
              myPokemon: state.myPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, current_hp: target.current_hp }
                  : p,
              ),
              opponentPokemon: state.opponentPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, current_hp: target.current_hp }
                  : p,
              ),
            }));
          }
        }
        break;
      }

      case 'status_applied': {
        if (targetId) {
          const target = snapshot.pokemon_instances.find(
            (p) => p.instance_id === targetId,
          );
          if (target) {
            set((state) => ({
              myPokemon: state.myPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, status: target.status }
                  : p,
              ),
              opponentPokemon: state.opponentPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, status: target.status }
                  : p,
              ),
            }));
          }
        }
        break;
      }

      case 'volatile_status_applied':
      case 'volatile_status_expired': {
        if (targetId) {
          const target = snapshot.pokemon_instances.find(
            (p) => p.instance_id === targetId,
          );
          if (target) {
            set((state) => ({
              myPokemon: state.myPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, volatile_status: target.volatile_status }
                  : p,
              ),
              opponentPokemon: state.opponentPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, volatile_status: target.volatile_status }
                  : p,
              ),
            }));
          }
        }
        break;
      }

      case 'stat_changed': {
        if (targetId) {
          const target = snapshot.pokemon_instances.find(
            (p) => p.instance_id === targetId,
          );
          if (target) {
            set((state) => ({
              myPokemon: state.myPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, stages: target.stages }
                  : p,
              ),
              opponentPokemon: state.opponentPokemon.map((p) =>
                p.instance_id === targetId
                  ? { ...p, stages: target.stages }
                  : p,
              ),
            }));
          }
        }
        break;
      }

      case 'pokemon_fainted': {
        if (targetId) {
          set((state) => ({
            myPokemon: state.myPokemon.map((p) =>
              p.instance_id === targetId ? { ...p, fainted: true } : p,
            ),
            opponentPokemon: state.opponentPokemon.map((p) =>
              p.instance_id === targetId ? { ...p, fainted: true } : p,
            ),
          }));
        }
        break;
      }

      case 'switch':
      case 'switch_in':
      case 'replacement': {
        set({ sides: snapshot.sides });
        break;
      }

      case 'weather_changed': {
        set({ weather: snapshot.weather });
        break;
      }

      case 'battle_finished': {
        set({
          status: 'finished',
          winnerTrainerId: snapshot.result?.winner_trainer_id ?? null,
          playerPhase: 'finished',
          turnQueue: [],
        });
        break;
      }

      default:
        break;
    }

    set((state) => ({
      myPokemon: state.myPokemon.map((p) => {
        const snapPokemon = snapshot.pokemon_instances.find(
          (s) => s.instance_id === p.instance_id,
        );
        return snapPokemon
          ? {
              ...p,
              move_state: snapPokemon.move_state,
              revealed_moves: snapPokemon.revealed_moves,
            }
          : p;
      }),
      opponentPokemon: state.opponentPokemon.map((p) => {
        const snapPokemon = snapshot.pokemon_instances.find(
          (s) => s.instance_id === p.instance_id,
        );
        return snapPokemon
          ? {
              ...p,
              move_state: snapPokemon.move_state,
              revealed_moves: snapPokemon.revealed_moves,
            }
          : p;
      }),
    }));
  },

  finalizeTurnAnimation: () => {
    if (get().status === 'finished') return;

    const { turnQueue, turnHistory, trainerId } = get();

    const newQueue = [...turnQueue];
    const nextTurn = newQueue.shift();

    if (newQueue.length > 0) {
      set({
        turnQueue: newQueue,
        turnHistory: nextTurn ? [...turnHistory, nextTurn] : turnHistory,
        playerPhase: 'animating',
      });
      return;
    }

    const processedTurn = turnHistory[turnHistory.length - 1];
    const requiredReplacements = processedTurn?.required_replacements ?? [];
    const myReplacements = requiredReplacements.find(
      (r) => r.trainer_id === trainerId,
    );

    if (myReplacements && myReplacements.available_instance_ids.length > 0) {
      set({
        turnQueue: newQueue,
        playerPhase: 'awaiting_switch',
        availableSwitches: myReplacements.available_instance_ids,
        turnHistory: nextTurn ? [...turnHistory, nextTurn] : turnHistory,
      });
    } else {
      set({
        turnQueue: newQueue,
        playerPhase: 'can_act',
        availableSwitches: [],
        turnHistory: nextTurn ? [...turnHistory, nextTurn] : turnHistory,
      });
    }
  },
}));