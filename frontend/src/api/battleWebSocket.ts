import type {
  ConnectionRequest,
  ConnectionResponse,
  TurnAction,
  BattleTurnDTO,
  ErrorPayload,
  WSMessage,
} from '../types/schemas/Battle';

export type ConnectionCallbacks = {
  onConnectionResponse: (response: ConnectionResponse) => void;
  onTurnResult: (turn: BattleTurnDTO) => void;
  onError: (error: ErrorPayload) => void;
};

export class BattleWebSocket {
  private ws: WebSocket | null = null;
  private callbacks: ConnectionCallbacks | null = null;

  connect(request: ConnectionRequest, callbacks: ConnectionCallbacks): void {
    this.callbacks = callbacks;
    this.ws = new WebSocket('ws://localhost:8000/ws');

    this.ws.onopen = () => {
      this.ws?.send(
        JSON.stringify({
          address: 'connection:request',
          payload: request,
        }),
      );
    };

    this.ws.onmessage = (event) => {
      const message: WSMessage = JSON.parse(event.data);

      switch (message.address) {
        case 'connection:response':
          this.callbacks?.onConnectionResponse(message.payload);
          break;
        case 'turn:result': {
          this.callbacks?.onTurnResult(message.payload);
          break;
        }

        case 'error':
          this.callbacks?.onError(message.payload);
          break;
      }
    };

    this.ws.onerror = () => {
      this.callbacks?.onError({
        code: 'WS_ERROR',
        message: 'WebSocket connection error',
      });
    };

    this.ws.onclose = () => {
      this.callbacks = null;
    };
  }

  sendTurnSubmit(trainerId: string, action: TurnAction): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          address: 'turn:submit',
          payload: { trainer_id: trainerId, action },
        }),
      );
    }
  }

  disconnect(): void {
    this.ws?.close();
    this.ws = null;
    this.callbacks = null;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}
