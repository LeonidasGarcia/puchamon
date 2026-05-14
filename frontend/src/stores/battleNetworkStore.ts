import { create } from 'zustand';
import { BattleWebSocket, type ConnectionCallbacks } from '../api/battleWebSocket';
import { useGameStore } from './gameStore';
import type {
  ConnectionRequest,
  ConnectionResponse,
  BattleTurnDTO,
  TurnAction,
  ErrorPayload,
  PokemonInstanceSnapshot,
  Player,
} from '../types/schemas/Battle';

interface BattleNetworkState {
  isConnected: boolean;
  battleId: string | null;
  trainerId: string | null;
  _ws: BattleWebSocket | null;
  lastError: ErrorPayload | null;
  connect: (request: ConnectionRequest) => void;
  disconnect: () => void;
  sendAction: (action: TurnAction) => void;
  _handleConnectionResponse: (response: ConnectionResponse) => void;
  _handleTurnResult: (turn: BattleTurnDTO) => void;
  _handleError: (error: ErrorPayload) => void;
}

const _callbacks: ConnectionCallbacks = {
  onConnectionResponse: () => {},
  onTurnResult: () => {},
  onError: () => {},
};

function extractMyPokemon(
  pokemonInstances: PokemonInstanceSnapshot[],
  trainerId: string,
): PokemonInstanceSnapshot[] {
  return pokemonInstances.filter((p) => p.trainer_id === trainerId);
}

function extractOpponentPokemon(
  pokemonInstances: PokemonInstanceSnapshot[],
  trainerId: string,
): PokemonInstanceSnapshot[] {
  return pokemonInstances.filter((p) => p.trainer_id !== trainerId);
}

export const useBattleNetworkStore = create<BattleNetworkState>((set, get) => ({
  isConnected: false,
  battleId: null,
  trainerId: null,
  _ws: null,
  lastError: null,

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
      battleId: null,
      trainerId: null,
      _ws: null,
      lastError: null,
    });
    useGameStore.getState().reset();
  },

  sendAction: (action: TurnAction) => {
    const { trainerId, _ws } = get();
    if (trainerId && _ws?.isConnected()) {
      _ws.sendTurnSubmit(trainerId, action);
    }
  },

  _handleConnectionResponse: (response: ConnectionResponse) => {
    const { initial_state } = response;
    const snapshot = initial_state.post_turn_snapshot;
    const trainerId = response.trainer_id;

    const controllerType = snapshot.players.find(
      (p: Player) => p.trainer_id === trainerId,
    )?.controller_type ?? 'ai';

    useGameStore.getState().initialize({
      controllerType,
      trainerId,
      myPokemon: extractMyPokemon(snapshot.pokemon_instances, trainerId),
      opponentPokemon: extractOpponentPokemon(snapshot.pokemon_instances, trainerId),
      weather: snapshot.weather,
      sides: snapshot.sides,
      status: snapshot.status,
      players: snapshot.players,
    });

    set({
      isConnected: true,
      battleId: response.battle_id,
      trainerId,
    });
  },

  _handleTurnResult: (turn: BattleTurnDTO) => {
    useGameStore.getState().enqueueTurn(turn);
  },

  _handleError: (error: ErrorPayload) => {
    set({ lastError: error });
  },
}));