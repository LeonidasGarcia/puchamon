import { create } from 'zustand';
import {
  BattleWebSocket,
  type ConnectionCallbacks,
} from '../api/battleWebSocket';
import type {
  ConnectionRequest,
  ConnectionResponse,
  BattleTurnDTO,
  BattleSnapshot,
  PokemonInstanceSnapshot,
  Player,
  TurnAction,
  ErrorPayload,
} from '../types/schemas/Battle';

interface BattleState {
  isConnected: boolean;
  trainerId: string | null;
  battleId: string | null;
  battleType: '1v1' | '2v2' | '3v3' | null;
  currentTurn: number;
  status: 'active' | 'finished' | 'paused' | null;
  phase: string | null;
  players: Player[];
  weather: BattleSnapshot['weather'];
  sides: BattleSnapshot['sides'];
  myPokemon: PokemonInstanceSnapshot[];
  opponentPokemon: PokemonInstanceSnapshot[];
  turnHistory: BattleTurnDTO[];
  isMyTurn: boolean;
  awaitingSwitch: boolean;
  availableSwitches: string[];
  lastError: ErrorPayload | null;
  winnerTrainerId: string | null;
  _ws: BattleWebSocket | null;
  connect: (request: ConnectionRequest) => void;
  disconnect: () => void;
  submitAction: (action: TurnAction) => void;
  _handleConnectionResponse: (response: ConnectionResponse) => void;
  _handleTurnResult: (turn: BattleTurnDTO) => void;
  _handleError: (error: ErrorPayload) => void;
}

const _callbacks: ConnectionCallbacks = {
  onConnectionResponse: () => {},
  onTurnResult: () => {},
  onError: () => {},
};

export const useBattleStore = create<BattleState>((set, get) => ({
  isConnected: false,
  trainerId: null,
  battleId: null,
  battleType: null,
  currentTurn: 0,
  status: null,
  phase: null,
  players: [],
  weather: null,
  sides: {},
  myPokemon: [],
  opponentPokemon: [],
  turnHistory: [],
  isMyTurn: false,
  awaitingSwitch: false,
  availableSwitches: [],
  lastError: null,
  winnerTrainerId: null,
  _ws: null,

  connect: (request: ConnectionRequest) => {
    const ws = new BattleWebSocket();

    _callbacks.onConnectionResponse = (r) => get()._handleConnectionResponse(r);
    _callbacks.onTurnResult = (t) => get()._handleTurnResult(t);
    _callbacks.onError = (e) => get()._handleError(e);

    ws.connect(request, _callbacks);
    set({ _ws: ws });
  },

  disconnect: () => {
    get()._ws?.disconnect();
    set({
      isConnected: false,
      trainerId: null,
      battleId: null,
      battleType: null,
      currentTurn: 0,
      status: null,
      phase: null,
      players: [],
      weather: null,
      sides: {},
      myPokemon: [],
      opponentPokemon: [],
      turnHistory: [],
      isMyTurn: false,
      awaitingSwitch: false,
      availableSwitches: [],
      lastError: null,
      winnerTrainerId: null,
      _ws: null,
    });
  },

  submitAction: (action: TurnAction) => {
    const { trainerId, _ws } = get();
    if (trainerId && _ws?.isConnected()) {
      _ws.sendTurnSubmit(trainerId, action);
      set({ isMyTurn: false });
    }
  },

  _handleConnectionResponse: (response: ConnectionResponse) => {
    const { initial_state } = response;
    const snapshot = initial_state.post_turn_snapshot;
    const trainerId = response.trainer_id;

    const myPokemon: PokemonInstanceSnapshot[] = [];
    const opponentPokemon: PokemonInstanceSnapshot[] = [];

    snapshot.pokemon_instances.forEach((pokemon) => {
      if (pokemon.trainer_id === trainerId) {
        myPokemon.push(pokemon);
      } else {
        opponentPokemon.push(pokemon);
      }
    });

    set({
      isConnected: true,
      trainerId: response.trainer_id,
      battleId: response.battle_id,
      battleType: response.battle_type,
      currentTurn: 0,
      status: snapshot.status,
      phase: snapshot.phase ?? null,
      players: snapshot.players,
      weather: snapshot.weather,
      sides: snapshot.sides,
      myPokemon,
      opponentPokemon,
      turnHistory: [],
      isMyTurn: true,
      awaitingSwitch: false,
      availableSwitches: [],
      lastError: null,
      winnerTrainerId: null,
    });
  },

  _handleTurnResult: (turn: BattleTurnDTO) => {
    const { trainerId } = get();
    const snapshot = turn.post_turn_snapshot;

    const newMyPokemon: PokemonInstanceSnapshot[] = [];
    const newOpponentPokemon: PokemonInstanceSnapshot[] = [];

    snapshot.pokemon_instances.forEach((pokemon) => {
      if (pokemon.trainer_id === trainerId) {
        newMyPokemon.push(pokemon);
      } else {
        newOpponentPokemon.push(pokemon);
      }
    });

    const awaitingSwitch = turn.required_replacements.length > 0;
    const availableSwitches = awaitingSwitch
      ? (turn.required_replacements.find((r) => r.trainer_id === trainerId)
          ?.available_instance_ids ?? [])
      : [];

    set({
      currentTurn: snapshot.turn,
      status: snapshot.status,
      phase: snapshot.phase ?? null,
      weather: snapshot.weather,
      sides: snapshot.sides,
      myPokemon: newMyPokemon,
      opponentPokemon: newOpponentPokemon,
      turnHistory: [...get().turnHistory, turn],
      isMyTurn: snapshot.status !== 'finished',
      awaitingSwitch,
      availableSwitches,
      winnerTrainerId: snapshot.result?.winner_trainer_id ?? null,
    });
  },

  _handleError: (error: ErrorPayload) => {
    set({ lastError: error });
  },
}));