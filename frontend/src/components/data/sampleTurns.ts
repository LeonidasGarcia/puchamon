import type { BattleTurnDTO } from "../../types/schemas/Battle";

function createSampleEvent(
  order: number,
  kind: string,
  message: string,
  source?: string,
  target?: string
) {
  return {
    order,
    kind,
    message,
    source_instance_id: source ?? null,
    target_instance_id: target ?? null,
    move_id: null,
    value: null,
    status_id: null,
    hazard_id: null,
    weather_id: null,
  };
}

function createSampleTurn(
  turn: number,
  eventsData: Array<{ order: number; kind: string; message: string; source?: string; target?: string }>
): BattleTurnDTO {
  return {
    battle_id: "sample-battle",
    turn,
    declared_actions: [],
    executed_actions: [],
    events: eventsData.map((e) => createSampleEvent(e.order, e.kind, e.message, e.source, e.target)),
    fainted_instance_ids: eventsData
      .filter((e) => e.kind === "pokemon_fainted")
      .map((e) => e.target ?? ""),
    required_replacements: [],
    post_turn_snapshot: {
      battle_id: "sample-battle",
      battle_type: "1v1" as const,
      turn,
      status: turn < 10 ? "active" as const : "finished" as const,
      phase: null,
      weather: turn >= 5 ? null : { weather_id: "rain", remaining_turns: 5 - turn, source_move_id: null },
      players: [
        { trainer_id: "p1", name: "Leo", controller_type: "human" as const, ai_level: null },
        { trainer_id: "p2", name: "Nick", controller_type: "ai" as const, ai_level: 2 },
      ],
      sides: {
        p1: { hazards: ["spikes", "stealth-rock"], active_pokemon_instance_ids: ["p1-pikachu"] },
        p2: { hazards: [], active_pokemon_instance_ids: ["p2-pidgey"] },
      },
      pokemon_instances: [
        {
          instance_id: "p1-pikachu",
          trainer_id: "p1",
          team_slot: 0,
          pokemon_id: "pikachu",
          level: 100,
          current_hp: turn < 3 ? 280 : 150,
          max_hp: 350,
          status: null,
          volatile_status: [],
          stages: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, acc: 0, eva: 0 },
          move_state: [
            { move_id: "thunderbolt", current_pp: 15 },
            { move_id: "quick-attack", current_pp: 30 },
            { move_id: "iron-tail", current_pp: 15 },
            { move_id: "thunder-wave", current_pp: 20 },
          ],
          fainted: false,
          is_revealed: true,
          revealed_moves: ["thunderbolt", "quick-attack", "iron-tail", "thunder-wave"],
        },
        {
          instance_id: "p2-pidgey",
          trainer_id: "p2",
          team_slot: 0,
          pokemon_id: "pidgey",
          level: 85,
          current_hp: turn === 4 ? 0 : 200,
          max_hp: 220,
          status: turn === 2 ? "paralysis" : null,
          volatile_status: [],
          stages: { atk: 0, def: 0, spa: 0, spd: 0, spe: 0, acc: 0, eva: 0 },
          move_state: [
            { move_id: "fly", current_pp: 10 },
            { move_id: "quick-attack", current_pp: 25 },
            { move_id: "roost", current_pp: 15 },
            { move_id: "toxic", current_pp: 10 },
          ],
          fainted: turn === 4,
          is_revealed: true,
          revealed_moves: ["fly", "quick-attack", "roost", "toxic"],
        },
      ],
      result: turn === 10 ? { winner_trainer_id: "p1", reason: "knockout" as const } : null,
    },
  };
}

export const SAMPLE_TURNS: BattleTurnDTO[] = [
  createSampleTurn(1, [
    { order: 1, kind: "move", message: "¡Pikachu usa Thunder!", source: "p1-pikachu", target: "p2-pidgey" },
    { order: 2, kind: "damage", message: "¡Es muy efectivo!", target: "p2-pidgey" },
    { order: 3, kind: "damage", message: "Pidgey perdió 85 PS", target: "p2-pidgey" },
  ]),
  createSampleTurn(2, [
    { order: 1, kind: "move", message: "¡Pidgey usa Toxic!", source: "p2-pidgey", target: "p1-pikachu" },
    { order: 2, kind: "status_applied", message: "¡Pikachu fue envenenado!", target: "p1-pikachu" },
  ]),
  createSampleTurn(3, [
    { order: 1, kind: "move", message: "¡Pikachu usa Quick Attack!", source: "p1-pikachu", target: "p2-pidgey" },
    { order: 2, kind: "damage", message: "Pidgey perdió 35 PS", target: "p2-pidgey" },
    { order: 3, kind: "move", message: "¡Pidgey usa Quick Attack!", source: "p2-pidgey", target: "p1-pikachu" },
    { order: 4, kind: "damage", message: "Pikachu perdió 40 PS", target: "p1-pikachu" },
    { order: 5, kind: "damage", message: "Pikachu perdió 15 PS por veneno", target: "p1-pikachu" },
  ]),
  createSampleTurn(4, [
    { order: 1, kind: "move", message: "¡Pikachu usa Iron Tail!", source: "p1-pikachu", target: "p2-pidgey" },
    { order: 2, kind: "damage", message: "Pidgey perdió 90 PS", target: "p2-pidgey" },
    { order: 3, kind: "pokemon_fainted", message: "¡Pidgey se debilitó!", target: "p2-pidgey" },
  ]),
  createSampleTurn(5, [
    { order: 1, kind: "switch", message: "¡Nick envío a Gastly!", source: "p2-gastly" },
    { order: 2, kind: "move", message: "¡Pikachu usa Thunder!", source: "p1-pikachu", target: "p2-gastly" },
    { order: 3, kind: "damage", message: "¡Es poco efectivo...", target: "p2-gastly" },
    { order: 4, kind: "damage", message: "Gastly perdió 45 PS", target: "p2-gastly" },
    { order: 5, kind: "weather_started", message: "La lluvia intensa sezio!" },
  ]),
  createSampleTurn(6, [
    { order: 1, kind: "move", message: "¡Gastly usa Shadow Ball!", source: "p2-gastly", target: "p1-pikachu" },
    { order: 2, kind: "damage", message: "Pikachu perdió 70 PS", target: "p1-pikachu" },
    { order: 3, kind: "damage", message: "Pikachu perdió 15 PS por veneno", target: "p1-pikachu" },
    { order: 4, kind: "move", message: "¡Pikachu usa Thunder!", source: "p1-pikachu", target: "p2-gastly" },
    { order: 5, kind: "damage", message: "Gastly perdió 60 PS", target: "p2-gastly" },
    { order: 6, kind: "weather_ended", message: "La lluvia intensa terminó" },
  ]),
  createSampleTurn(7, [
    { order: 1, kind: "move", message: "¡Gastly usa Sucker Punch!", source: "p2-gastly", target: "p1-pikachu" },
    { order: 2, kind: "move", message: "¡Pikachu no se movió a tiempo!", target: "p1-pikachu" },
    { order: 3, kind: "damage", message: "Pikachu perdió 55 PS", target: "p1-pikachu" },
    { order: 4, kind: "damage", message: "Pikachu perdió 15 PS por veneno", target: "p1-pikachu" },
  ]),
  createSampleTurn(8, [
    { order: 1, kind: "move", message: "¡Pikachu usa Thunder Wave!", source: "p1-pikachu", target: "p2-gastly" },
    { order: 2, kind: "status_applied", message: "¡Gastly quedó paralizado!", target: "p2-gastly" },
    { order: 3, kind: "move", message: "¡Gastly usa Shadow Ball!", source: "p2-gastly", target: "p1-pikachu" },
    { order: 4, kind: "damage", message: "Pikachu perdió 65 PS", target: "p1-pikachu" },
    { order: 5, kind: "damage", message: "Pikachu perdió 15 PS por veneno", target: "p1-pikachu" },
  ]),
  createSampleTurn(9, [
    { order: 1, kind: "move", message: "¡Pikachu usa Thunder!", source: "p1-pikachu", target: "p2-gastly" },
    { order: 2, kind: "damage", message: "Gastly perdió 80 PS", target: "p2-gastly" },
    { order: 3, kind: "pokemon_fainted", message: "¡Gastly se debilitó!", target: "p2-gastly" },
  ]),
  createSampleTurn(10, [
    { order: 1, kind: "switch", message: "¡Nick envío a Eevee!", source: "p2-eevee" },
    { order: 2, kind: "move", message: "¡Pikachu usa Quick Attack!", source: "p1-pikachu", target: "p2-eevee" },
    { order: 3, kind: "damage", message: "Eevee perdió 40 PS", target: "p2-eevee" },
    { order: 4, kind: "move", message: "¡Eevee usa Quick Attack!", source: "p2-eevee", target: "p1-pikachu" },
    { order: 5, kind: "damage", message: "Pikachu perdió 35 PS", target: "p1-pikachu" },
    { order: 6, kind: "damage", message: "Pikachu perdió 15 PS por veneno", target: "p1-pikachu" },
    { order: 7, kind: "move", message: "¡Pikachu usa Iron Tail!", source: "p1-pikachu", target: "p2-eevee" },
    { order: 8, kind: "damage", message: "Eevee perdió 85 PS", target: "p2-eevee" },
    { order: 9, kind: "pokemon_fainted", message: "¡Eevee se debilitó!", target: "p2-eevee" },
    { order: 10, kind: "battle_finished", message: "¡Leo gana la batalla!" },
  ]),
];