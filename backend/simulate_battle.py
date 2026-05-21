"""Script to simulate a battle turn for testing purposes."""

import asyncio

from loguru import logger

from puchamon.modules.battle.application.services.battle_setup_service import BattleSetupService
from puchamon.modules.battle.application.services.turn_resolution_service import (
    TurnResolutionService,
    _ResolveTurnParams,
)
from puchamon.modules.battle.domain.entities import Player, TargetScope, TurnAction
from puchamon.modules.battle.domain.registries import (
    build_default_action_strategy_registry,
    build_default_condition_effect_strategy_registry,
    build_default_move_effect_strategy_registry,
)
from puchamon.modules.pokedex.domain.entities import Condition, MoveEffect, Movement, Moveset, Pokemon, Type
from puchamon.shared.infrastructure.database import init_db


async def simulate():
    """Simulate a single battle turn with random pokemon and human/AI players."""
    await init_db()
    logger.info("Database initialized.")

    players = [
        Player(trainer_id="player_1", name="Trainer Red", controller_type="human"),
        Player(trainer_id="player_2", name="Trainer Blue", controller_type="ai"),
    ]

    logger.info("Creating battle with random pokemon...")
    battle, instances = await BattleSetupService.create_battle(battle_type="1v1", players=players, team_size=3)

    instance_dict = {inst.id: inst for inst in instances}

    p1_active_id = battle.sides["player_1"].active_pokemon_instance_ids[0]
    p2_active_id = battle.sides["player_2"].active_pokemon_instance_ids[0]

    p1_pokemon = instance_dict[p1_active_id]
    p2_pokemon = instance_dict[p2_active_id]

    logger.info(f"Battle Started! {p1_pokemon.pokemon_id} vs {p2_pokemon.pokemon_id}")
    logger.info(f"P1 HP: {p1_pokemon.current_hp}/{p1_pokemon.max_hp}")
    logger.info(f"P2 HP: {p2_pokemon.current_hp}/{p2_pokemon.max_hp}")

    turn_service = TurnResolutionService(
        action_registry=build_default_action_strategy_registry(),
        move_effect_registry=build_default_move_effect_strategy_registry(),
        condition_effect_registry=build_default_condition_effect_strategy_registry(),
    )

    p1_move_id = p1_pokemon.move_state[0].move_id
    p2_move_id = p2_pokemon.move_state[0].move_id

    actions = [
        TurnAction(
            player="player_1",
            type="move",
            user_instance_id=p1_active_id,
            move_id=p1_move_id,
            target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0),
        ),
        TurnAction(
            player="player_2",
            type="move",
            user_instance_id=p2_active_id,
            move_id=p2_move_id,
            target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0),
        ),
    ]

    logger.info("Loading move and condition data for resolution...")

    move_count = await Movement.count()
    poke_count = await Pokemon.count()
    mset_count = await Moveset.count()
    logger.debug(f"DB Status: {move_count} movements, {poke_count} pokemons, {mset_count} movesets")

    if mset_count > 0:
        sample_mset = await Moveset.find_one()
        logger.debug(f"Sample moveset: {sample_mset}")

    movements = {m.id: m for m in await Movement.find_all().to_list()}
    logger.debug(f"Loaded {len(movements)} movements. First 5 keys: {list(movements.keys())[:5]}")
    conditions = {c.id: c for c in await Condition.find_all().to_list()}
    types = {t.id: t for t in await Type.find_all().to_list()}
    move_effects = {e.id: e for e in await MoveEffect.find_all().to_list()}

    logger.info("--- Resolving Turn 1 ---")
    logger.info(f"P1 Action: {p1_pokemon.pokemon_id} uses {p1_move_id}")
    logger.info(f"P2 Action: {p2_pokemon.pokemon_id} uses {p2_move_id}")

    context = turn_service.resolve_turn(
        _ResolveTurnParams(
            battle=battle,
            instances=instance_dict,
            actions=actions,
            movements=movements,
            conditions=conditions,
            move_effects=move_effects,
            type_chart=types,
        )
    )

    for event in context.events:
        logger.info(f"[{event.kind}] {event.message}")

    logger.info(f"Turn End. P1 HP: {p1_pokemon.current_hp}/{p1_pokemon.max_hp}")
    logger.info(f"Turn End. P2 HP: {p2_pokemon.current_hp}/{p2_pokemon.max_hp}")
    logger.info(f"Next Turn: {battle.turn}, Phase: {battle.phase}")


if __name__ == "__main__":
    asyncio.run(simulate())
