"""Service for handling battle-related logic and lifecycle."""

from typing import Any

from loguru import logger

from ....agentia.application.services import IAService
from ....pokedex.domain.entities import Condition, MoveEffect, Movement, Type, Weather
from ...domain.entities import Battle, BattleInstance, Player, TurnAction
from ...domain.registries import (
    build_default_action_strategy_registry,
    build_default_condition_effect_strategy_registry,
    build_default_move_effect_strategy_registry,
    build_default_weather_effect_strategy_registry,
)
from ...domain.runtime.context import BattleStrategyContext
from ..mappers.battle_snapshot_mapper import to_battle_snapshot_dto
from ..mappers.battle_turn_mapper import map_context_to_turn_dto
from .battle_setup_service import BattleSetupService
from .turn_resolution_service import TurnResolutionService


class BattleService:
    """Application service that acts as the entry point for Battle use cases.

    It orchestrates the flow between the database, setup, and turn resolution.
    It provides a clean facade that WebSocket and HTTP endpoints should use,
    hiding all internal complexity (IAService, TurnResolutionService, registries, etc.).
    """

    def __init__(self) -> None:
        self._ia_service = IAService()
        self._turn_service = TurnResolutionService(
            action_registry=build_default_action_strategy_registry(),
            move_effect_registry=build_default_move_effect_strategy_registry(),
            condition_effect_registry=build_default_condition_effect_strategy_registry(),
            weather_effect_registry=build_default_weather_effect_strategy_registry(),
        )
        self._data_cache: dict[str, Any] = {}

    async def _load_pokedex_data(self) -> dict[str, Any]:
        """Load and cache Pokédex data needed for turn resolution."""
        if not self._data_cache:
            movements = {m.id: m for m in await Movement.find_all().to_list()}
            conditions = {c.id: c for c in await Condition.find_all().to_list()}
            types = {t.id: t for t in await Type.find_all().to_list()}
            move_effects = {e.id: e for e in await MoveEffect.find_all().to_list()}
            weathers = {w.id: w for w in await Weather.find_all().to_list()}
            self._data_cache = {
                "movements": movements,
                "conditions": conditions,
                "types": types,
                "move_effects": move_effects,
                "weathers": weathers,
            }
        return self._data_cache

    async def create_battle(
        self,
        battle_type: str,
        players: list[Player],
        team_size: int = 3,
    ) -> tuple[Battle, list[BattleInstance]]:
        """Creates a new battle with random Pokemon for each player.

        Args:
            battle_type: Type of battle ("1v1", "2v2", "3v3").
            players: List of players (human or AI).
            team_size: Number of Pokemon per team.

        Returns:
            A tuple of (Battle, list of BattleInstance).
        """
        battle, instances = await BattleSetupService.create_battle(
            battle_type=battle_type,
            players=players,
            team_size=team_size,
        )

        await battle.save()
        for instance in instances:
            await instance.save()

        logger.info(f"Battle {battle.id} created with {len(instances)} instances")
        return battle, instances

    async def submit_action(
        self,
        battle_id: str,
        trainer_id: str,
        action: TurnAction,
    ) -> dict[str, Any]:
        """Process a single turn when a player submits an action.

        If the player is AI, generates their action automatically.
        Resolves the turn and returns a BattleTurnDTO with all events.

        Args:
            battle_id: ID of the battle.
            trainer_id: ID of the trainer submitting the action.
            action: The TurnAction submitted by the player.

        Returns:
            A dict containing battle_id, turn, and the BattleTurnDTO.
        """
        battle = await Battle.get(battle_id)
        if not battle:
            raise ValueError(f"Battle {battle_id} not found")

        trainer_ids = [p.trainer_id for p in battle.players]
        if trainer_id not in trainer_ids:
            raise ValueError(f"Trainer {trainer_id} not in battle")

        instances_list = await BattleInstance.find_all().to_list()
        instances = {str(inst.id): inst for inst in instances_list}

        actions = list(battle.current_turn_actions)
        actions.append(action)

        for player in battle.players:
            if player.trainer_id == trainer_id:
                continue
            if player.controller_type == "ai":
                ai_action = await self._ia_service.generate_action(
                    player=player,
                    battle=battle,
                    instances=instances,
                )
                actions.append(ai_action)

        data = await self._load_pokedex_data()
        context: BattleStrategyContext = self._turn_service.resolve_turn(
            battle=battle,
            instances=instances,
            actions=actions,
            movements=data["movements"],
            conditions=data["conditions"],
            weathers=data["weathers"],
            move_effects=data["move_effects"],
            type_chart=data["types"],
        )

        battle.current_turn_actions = []
        await battle.save()
        for instance in instances.values():
            await instance.save()

        ordered_actions = self._sort_actions_for_dto(actions)

        turn_dto = map_context_to_turn_dto(
            battle=battle,
            declared_actions=actions,
            executed_actions=ordered_actions,
            context=context,
        )

        return {
            "battle_id": battle_id,
            "turn": battle.turn,
            "turn_data": turn_dto,
        }

    def _sort_actions_for_dto(
        self,
        actions: list[TurnAction],
    ) -> list[TurnAction]:
        """Return actions in execution order for the DTO."""
        move_actions = [a for a in actions if a.type == "move"]
        switch_actions = [a for a in actions if a.type == "switch"]
        return switch_actions + move_actions

    async def get_battle(self, battle_id: str) -> Battle | None:
        """Retrieves a battle from the database."""
        return await Battle.get(battle_id)

    async def get_battle_snapshot(self, battle_id: str) -> dict[str, Any] | None:
        """Get a battle snapshot for the client.

        Returns a dict with battle info and all instances,
        suitable for sending to the client via WebSocket.
        """
        battle = await Battle.get(battle_id)
        if not battle:
            return None

        instances_list = await BattleInstance.find_all().to_list()

        return {
            "battle_id": str(battle.id),
            "battle_type": battle.battle_type,
            "turn": battle.turn,
            "status": battle.status,
            "phase": battle.phase,
            "players": [p.model_dump() for p in battle.players],
            "sides": {k: v.model_dump() for k, v in battle.sides.items()},
            "pokemon_instances": [
                to_battle_snapshot_dto(battle, instances_list).model_dump()
            ],
            "result": battle.result.model_dump() if battle.result else None,
        }

    async def forfeit_battle(self, battle_id: str, trainer_id: str) -> dict[str, Any]:
        """Ends the battle immediately because a player surrendered."""
        battle = await Battle.get(battle_id)
        if not battle:
            raise ValueError(f"Battle {battle_id} not found")

        trainer_ids = [p.trainer_id for p in battle.players]
        if trainer_id not in trainer_ids:
            raise ValueError(f"Trainer {trainer_id} not in battle")

        battle.status = "finished"
        battle.result = {"winner_trainer_id": trainer_id, "reason": "forfeit"}
        await battle.save()

        return {
            "battle_id": battle_id,
            "status": "finished",
            "result": battle.result,
        }
