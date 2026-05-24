export interface WeatherState {
  weather_id: string;
  remaining_turns: number;
  source_move_id: string | null;
}

export interface Player {
  trainer_id: string;
  name: string;
  controller_type: "human" | "ai";
  ai_level: 1 | 2 | 3 | null;
}

export interface SideState {
  hazards: string[];
  active_pokemon_instance_ids: (string | null)[];
}

export interface StatStages {
  atk: number;
  def: number;
  spa: number;
  spd: number;
  spe: number;
  acc: number;
  eva: number;
}

export interface MoveStateSnapshot {
  move_id: string;
  current_pp: number;
}

export interface PokemonInstanceSnapshot {
  instance_id: string;
  trainer_id: string;
  team_slot: number;
  pokemon_id: string;
  level: number;
  current_hp: number;
  max_hp: number;
  status: string | null;
  volatile_status: string[];
  stages: StatStages;
  move_state: MoveStateSnapshot[];
  fainted: boolean;
  is_revealed: boolean;
  revealed_moves: string[];
}

export interface BattleResult {
  winner_trainer_id: string;
  reason: "knockout" | "forfeit" | "time";
}

export interface BattleSnapshot {
  battle_id: string;
  battle_type: "1v1" | "2v2" | "3v3";
  turn: number;
  status: "active" | "finished" | "paused";
  phase: "setup" | "awaiting_actions" | "resolving_turn" | "awaiting_replacements" | null;
  weather: WeatherState | null;
  players: Player[];
  sides: Record<string, SideState>;
  pokemon_instances: PokemonInstanceSnapshot[];
  result: BattleResult | null;
}

export interface TurnActionTarget {
  scope: "target" | "self" | "all" | "field" | "ally_party";
  target_side: "ally_side" | "foe_side" | null;
  target_active_slot: number | null;
}

export interface DeclaredTurnAction {
  trainer_id: string;
  action_type: "move" | "switch";
  user_instance_id: string;
  move_id: string | null;
  target: TurnActionTarget | null;
}

export interface ExecutedTurnAction {
  order: number;
  trainer_id: string;
  action_type: "move" | "switch";
  user_instance_id: string;
  move_id: string | null;
  target: TurnActionTarget | null;
  hit: boolean | null;
  skipped_reason: string | null;
  revealed_move: boolean;
}

export interface BattleTurnEvent {
  order: number;
  kind: string;
  source_instance_id: string | null;
  target_instance_id: string | null;
  move_id: string | null;
  value: number | null;
  status_id: string | null;
  hazard_id: string | null;
  weather_id: string | null;
  message: string;
}

export interface ForcedReplacement {
  trainer_id: string;
  active_slot: number;
  fainted_instance_id: string;
  available_instance_ids: string[];
}

export interface BattleTurnDTO {
  battle_id: string;
  turn: number;
  declared_actions: DeclaredTurnAction[];
  executed_actions: ExecutedTurnAction[];
  events: BattleTurnEvent[];
  fainted_instance_ids: string[];
  required_replacements: ForcedReplacement[];
  post_turn_snapshot: BattleSnapshot;
}

export interface TurnAction {
  type: "move" | "switch";
  user_instance_id: string;
  move_id: string | null;
  target: TurnActionTarget | null;
  replacement_instance_id: string | null;
}

export interface TurnSubmit {
  trainer_id: string;
  action: TurnAction;
}

export interface ConnectionRequest {
  name: string;
  controller_type: "human" | "ai";
  battle_type: "1v1" | "2v2" | "3v3";
  difficulty?: 1 | 2 | 3;
  ai2_difficulty?: 1 | 2 | 3;
}

export interface ConnectionResponse {
  trainer_id: string;
  battle_id: string;
  battle_type: "1v1" | "2v2" | "3v3";
  team_size: number;
  initial_state: BattleTurnDTO;
}

export interface ErrorPayload {
  code: string;
  message: string;
}

export type WSMessage =
  | { address: "connection:response"; payload: ConnectionResponse }
  | { address: "turn:result"; payload: BattleTurnDTO }
  | { address: "error"; payload: ErrorPayload };