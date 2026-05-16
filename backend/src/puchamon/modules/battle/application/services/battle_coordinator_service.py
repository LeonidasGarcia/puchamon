"""Service for coordinating battles (Game Loop Orchestration)."""

from typing import Any

from loguru import logger

from ....agentia.application.services.ia_service import IAService
from ...domain.entities import Battle, BattleInstance, TurnAction
from .battle_service import BattleService


class BattleCoordinatorService:
    """Orchestrates battle flow between human players and AI.

    Acts as the Game Loop, requesting actions from AI, validating human input readiness,
    and invoking the core BattleService to execute turns.
    """

    def __init__(self, battle_service: BattleService, ia_service: IAService):
        self._battle_service = battle_service
        self._ia_service = ia_service

    async def submit_human_action(
        self,
        battle_id: str,
        trainer_id: str,
        action: TurnAction,
    ) -> list[dict[str, Any]]:
        """Process a human action, collect AI actions, and execute the turn.

        Returns a list of turn results (may contain more than one if AI auto-replaces).
        """
        battle = await self._battle_service.get_battle(battle_id)
        if not battle or battle.status == "finished":
            return []

        self._validate_trainer_and_action(battle, trainer_id, action)

        actions, instances, data = await self._prepare_actions_and_context(
            battle_id=battle_id,
            initial_action=action,
        )

        await self._append_ai_actions(battle, instances, data, actions)

        results: list[dict[str, Any]] = []

        await self._execute_phase_actions(battle_id, battle, actions, results)
        await self._process_auto_replacements(battle_id, results)

        return results

    def _validate_trainer_and_action(
        self,
        battle: Battle,
        trainer_id: str,
        action: TurnAction,
    ) -> None:
        """Validate that the trainer belongs to the battle and the action fits the phase."""
        trainer_ids = [p.trainer_id for p in battle.players]
        if trainer_id not in trainer_ids:
            raise ValueError(f"Trainer {trainer_id} not in battle")

        if battle.phase == "awaiting_replacements" and action.type != "switch":
            raise ValueError("Only switch actions are allowed during awaiting_replacements phase")

    async def _prepare_actions_and_context(
        self,
        battle_id: str,
        initial_action: TurnAction,
    ) -> tuple[list[TurnAction], dict[str, BattleInstance], dict[str, Any]]:
        """Prepare initial actions list, instances map, and pokedex data."""
        actions = [initial_action]
        instances_list = await BattleInstance.find_many({"battleId": battle_id}).to_list()
        instances = {str(inst.id): inst for inst in instances_list}
        data = await self._battle_service.get_pokedex_data()
        return actions, instances, data

    async def _append_ai_actions(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        data: dict[str, Any],
        actions: list[TurnAction],
    ) -> None:
        """Generate and append AI actions for all AI-controlled players."""
        for player in battle.players:
            if player.controller_type == "ai":
                ai_action = await self._generate_ai_action(player, battle, instances, data)
                if ai_action:
                    actions.append(ai_action)

    async def _execute_phase_actions(
        self,
        battle_id: str,
        battle: Battle,
        actions: list[TurnAction],
        results: list[dict[str, Any]],
    ) -> None:
        """Execute actions according to the current battle phase and collect results."""
        if battle.phase == "awaiting_actions":
            turn_result = await self._battle_service.execute_turn(battle_id, actions)
        elif battle.phase == "awaiting_replacements":
            turn_result = await self._battle_service.execute_replacements(battle_id, actions)
        else:
            turn_result = None

        if turn_result:
            results.append(turn_result)

    async def _process_auto_replacements(self, battle_id: str, results: list[dict[str, Any]]) -> None:
        """Check if we need auto-replacements for AI (if only AI fainted) and execute them."""
        battle = await self._battle_service.get_battle(battle_id)
        if not battle or battle.phase != "awaiting_replacements":
            return

        ai_replacements = []
        human_needs_replacement = False

        instances_list = await BattleInstance.find_many({"battleId": battle_id}).to_list()
        instances = {str(inst.id): inst for inst in instances_list}

        for player in battle.players:
            side = battle.sides.get(player.trainer_id)
            if not side or all(slot is not None for slot in side.active_pokemon_instance_ids):
                continue

            if player.controller_type == "human":
                human_needs_replacement = True
            else:
                ai_switch = await self._ia_service.generate_switch_action(
                    player=player,
                    battle=battle,
                    instances=instances,
                    ai_level=player.ai_level or 1,
                )
                if ai_switch:
                    ai_replacements.append(ai_switch)

        if not human_needs_replacement and ai_replacements:
            logger.info("[COORDINATOR] Auto-executing AI replacements since human doesn't need any.")
            replacement_result = await self._battle_service.execute_replacements(battle_id, ai_replacements)
            if replacement_result:
                results.append(replacement_result)

    async def _generate_ai_action(
        self,
        player,
        battle: Battle,
        instances: dict[str, BattleInstance],
        data: dict[str, Any],
    ) -> TurnAction | None:
        """Generate an action for an AI player depending on the phase."""
        if battle.phase == "awaiting_replacements":
            # Only generate switch if this specific AI needs it
            side = battle.sides.get(player.trainer_id)
            if side and any(slot is None for slot in side.active_pokemon_instance_ids):
                return await self._ia_service.generate_switch_action(
                    player=player,
                    battle=battle,
                    instances=instances,
                    ai_level=player.ai_level or 1,
                )
            return None

        return await self._ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=player.ai_level or 1,
            movements=data["movements"],
        )

    async def run_ai_vs_ai_loop(self, battle_id: str) -> list[dict[str, Any]]:
        """Execute a full AI vs AI battle, returning all turn results."""
        results = []

        while True:
            battle = await self._battle_service.get_battle(battle_id)
            if not battle or battle.status == "finished":
                break

            instances_list = await BattleInstance.find_many({"battleId": battle_id}).to_list()
            instances = {str(inst.id): inst for inst in instances_list}
            data = await self._battle_service.get_pokedex_data()

            actions = []
            for player in battle.players:
                if player.controller_type == "ai":
                    ai_action = await self._generate_ai_action(player, battle, instances, data)
                    if ai_action:
                        actions.append(ai_action)

            if battle.phase == "awaiting_actions":
                result = await self._battle_service.execute_turn(battle_id, actions)
            else:
                result = await self._battle_service.execute_replacements(battle_id, actions)

            if result:
                results.append(result)

            battle = await self._battle_service.get_battle(battle_id)
            if not battle or battle.status == "finished":
                break

        return results
