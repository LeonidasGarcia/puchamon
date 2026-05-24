"""Service for handling battle-related logic and lifecycle."""

from typing import Any, Literal, cast

from bson import ObjectId
from loguru import logger

from ....pokedex.domain.entities import Condition, MoveEffect, Movement, Type
from ...domain.entities import Battle, BattleInstance, Player, TurnAction
from ...domain.exceptions import BattleValidationError
from ...domain.registries import (
    build_default_action_strategy_registry,
    build_default_condition_effect_strategy_registry,
    build_default_move_effect_strategy_registry,
)
from ...domain.runtime.context import ActionExecutionInput, BattleStrategyContext
from ..dto.battle_turn_dto import BattleTurnDTO
from ..mappers.battle_snapshot_mapper import to_battle_snapshot_dto
from ..mappers.battle_turn_mapper import map_context_to_turn_dto
from .battle_setup_service import BattleSetupService
from .turn_resolution_service import TurnResolutionService, _ResolveTurnParams


class BattleService:
    """Application service that acts as the entry point for Battle use cases.

    It orchestrates the flow between the database, setup, and turn resolution.
    It provides a clean facade that WebSocket and HTTP endpoints should use,
    hiding all internal complexity (IAService, TurnResolutionService, registries, etc.).
    """

    def __init__(self) -> None:
        self._turn_service = TurnResolutionService(
            action_registry=build_default_action_strategy_registry(),
            move_effect_registry=build_default_move_effect_strategy_registry(),
            condition_effect_registry=build_default_condition_effect_strategy_registry(),
        )
        self._data_cache: dict[str, Any] = {}

    async def get_pokedex_data(self) -> dict[str, Any]:
        """Load and cache Pokédex data needed for turn resolution."""
        if not self._data_cache:
            movements = {m.id: m for m in await Movement.find_all().to_list()}
            conditions = {c.id: c for c in await Condition.find_all().to_list()}
            types = {t.id: t for t in await Type.find_all().to_list()}
            move_effects = {e.id: e for e in await MoveEffect.find_all().to_list()}
            self._data_cache = {
                "movements": movements,
                "conditions": conditions,
                "types": types,
                "move_effects": move_effects,
            }
        return self._data_cache

    async def create_battle(
        self,
        trainer_name: str,
        controller_type: Literal["human", "ai"],
        battle_type: Literal["1v1", "2v2", "3v3"],
        difficulty: int = 1,
        ai2_difficulty: int | None = None,
    ) -> tuple[Battle, list[BattleInstance]]:
        """Creates a new battle with random Pokemon for each player.

        Args:
            trainer_name: Name of the human player (or first AI in AI vs AI).
            controller_type: "human" for Player vs AI, "ai" for AI vs AI.
            battle_type: Type of battle ("1v1", "2v2", "3v3").
            difficulty: AI difficulty level (1=easy, 2=medium, 3=hard). Only used when controller_type is "human".

        Returns:
            A tuple of (Battle, list of BattleInstance).
        """
        trainer_id = str(ObjectId())

        client_player = Player(
            trainer_id=trainer_id,
            name=trainer_name,
            controller_type=controller_type,
            ai_level=None,
        )

        if controller_type == "human":
            opponent = Player(
                trainer_id=str(ObjectId()),
                name="AI Opponent",
                controller_type="ai",
                ai_level=cast("Literal[1, 2, 3]", difficulty),
            )
            players = [client_player, opponent]
        else:
            ai_player_1 = Player(
                trainer_id=str(ObjectId()),
                name="AI Player 1",
                controller_type="ai",
                ai_level=cast("Literal[1, 2, 3]", difficulty),
            )
            ai_player_2 = Player(
                trainer_id=str(ObjectId()),
                name="AI Player 2",
                controller_type="ai",
                ai_level=cast("Literal[1, 2, 3]", ai2_difficulty if ai2_difficulty is not None else difficulty),
            )
            players = [ai_player_1, ai_player_2]

        team_size = int(battle_type[0])

        data = await self.get_pokedex_data()

        battle, instances = await BattleSetupService.create_battle(
            battle_type=battle_type,
            players=players,
            team_size=team_size,
            movements=data["movements"],
            move_effects=data["move_effects"],
        )

        await battle.save()
        for instance in instances:
            await instance.save()

        logger.info(f"Battle {battle.id} created with {len(instances)} instances")
        return battle, instances

    async def execute_turn(
        self,
        battle_id: str,
        actions: list[TurnAction],
    ) -> dict[str, Any] | None:
        """Process a full turn with the provided actions.

        Args:
            battle_id: ID of the battle.
            actions: List of TurnActions for this turn.

        Returns:
            A dict containing battle_id, turn, and the BattleTurnDTO.
            If battle is finished, returns the battle snapshot.
            If battle is not found, returns None.
        """
        battle = await Battle.get(battle_id)
        if not battle:
            return None

        if battle.status == "finished":
            return await self.get_battle_snapshot(battle_id)

        instances_list = await BattleInstance.find_many({"battleId": battle_id}).to_list()
        instances = {str(inst.id): inst for inst in instances_list}

        processed_turn = battle.turn

        # Ensure pokedex data is cached
        await self.get_pokedex_data()

        context = self._resolve_turn(battle, instances, actions)
        self._clear_turn_actions(battle)

        logger.info(f"[EXECUTE_TURN] phase={battle.phase}, turn={battle.turn}")

        if battle.phase == "awaiting_replacements":
            needs_replacement = any(slot is None for side in battle.sides.values() for slot in side.active_pokemon_instance_ids)
            if not needs_replacement:
                battle.turn += 1
                battle.phase = "awaiting_actions"
                logger.info(f"[EXECUTE_TURN] All replacements done, advancing to phase={battle.phase}, turn={battle.turn}")
        elif battle.status == "active":
            battle.turn += 1
            logger.info(f"[EXECUTE_TURN] Normal turn, advancing to turn={battle.turn}")

        await battle.save()
        for instance in instances.values():
            await instance.save()

        return self._build_turn_result(battle_id, processed_turn, actions, context)

    async def execute_replacements(
        self,
        battle_id: str,
        actions: list[TurnAction],
    ) -> dict[str, Any] | None:
        """Process replacement actions mid-turn or end-turn.

        Args:
            battle_id: ID of the battle.
            actions: List of switch TurnActions.

        Returns:
            A dict containing battle_id, turn, and the BattleTurnDTO.
        """
        battle = await Battle.get(battle_id)
        if not battle:
            return None

        if battle.status == "finished":
            return await self.get_battle_snapshot(battle_id)

        instances_list = await BattleInstance.find_many({"battleId": battle_id}).to_list()
        instances = {str(inst.id): inst for inst in instances_list}

        for action in actions:
            if action.type != "switch":
                raise BattleValidationError("Only switch actions are allowed during awaiting_replacements phase")

        context = BattleStrategyContext(battle=battle, battle_instances=instances)

        for action in actions:
            switch_strategy = self._turn_service._action_registry.get("switch")
            execution = ActionExecutionInput(action=action, replacement_instance_id=action.replacement_instance_id)
            switch_strategy.execute(context, execution)

        needs_replacement = any(slot is None for side in battle.sides.values() for slot in side.active_pokemon_instance_ids)
        if not needs_replacement:
            battle.turn += 1
            battle.phase = "awaiting_actions"
            logger.info(f"[EXECUTE_REPLACEMENTS] All replacements done, advancing to phase={battle.phase}, turn={battle.turn}")

        await battle.save()
        for instance in instances.values():
            await instance.save()

        return self._build_turn_result(battle_id, battle.turn, actions, context)

    def _resolve_turn(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        actions: list[TurnAction],
    ) -> BattleStrategyContext:
        """Resolve all actions for this turn."""
        data = self._data_cache
        params = _ResolveTurnParams(
            battle=battle,
            instances=instances,
            actions=actions,
            movements=data["movements"],
            conditions=data["conditions"],
            move_effects=data["move_effects"],
            type_chart=data["types"],
        )
        return self._turn_service.resolve_turn(params)

    def _clear_turn_actions(self, battle: Battle) -> None:
        """Clear the current turn actions buffer."""
        battle.current_turn_actions = []

    def _build_turn_result(
        self,
        battle_id: str,
        processed_turn: int,
        actions: list[TurnAction],
        context: BattleStrategyContext,
    ) -> dict[str, Any]:
        """Build the final turn result dictionary."""
        ordered_actions = self._sort_actions_for_dto(actions)
        turn_dto = map_context_to_turn_dto(
            battle=context.battle,
            declared_actions=actions,
            executed_actions=ordered_actions,
            context=context,
            turn=processed_turn,
        )
        return {
            "battle_id": battle_id,
            "turn": processed_turn,
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

    async def get_initial_state_dto(self, battle: Battle, instances: list[BattleInstance]) -> BattleTurnDTO:
        """Create the initial state DTO for a newly created battle."""
        return await BattleSetupService.get_initial_state_dto(battle, instances)

    async def get_battle_snapshot(self, battle_id: str) -> dict[str, Any] | None:
        """Get a battle snapshot for the client.

        Returns a dict with battle info and all instances,
        suitable for sending to the client via WebSocket.
        """
        battle = await Battle.get(battle_id)
        if not battle:
            return None

        instances_list = await BattleInstance.find_many({"battleId": battle_id}).to_list()

        return {
            "battle_id": str(battle.id),
            "battle_type": battle.battle_type,
            "turn": battle.turn,
            "status": battle.status,
            "phase": battle.phase,
            "players": [p.model_dump() for p in battle.players],
            "sides": {k: v.model_dump() for k, v in battle.sides.items()},
            "pokemon_instances": [to_battle_snapshot_dto(battle, instances_list).model_dump()],
            "result": battle.result.model_dump() if battle.result else None,
        }
