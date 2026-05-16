"""Service for executing AI vs AI battles."""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ....battle.application.services.battle_service import BattleService
from .ia_service import IAService


class BattleExecutionService:
    """Service for running AI vs AI battle loops."""

    def __init__(self, battle_service: "BattleService", ia_service: IAService):
        self._battle_service = battle_service
        self._ia_service = ia_service

    async def run_ai_vs_ai_loop(self, battle_id: str) -> list[dict[str, Any]]:
        """Execute a full AI vs AI battle, returning all turn results.

        Args:
            battle_id: ID of the battle to run.

        Returns:
            List of turn results, each containing turn_data.
        """
        results = []

        while True:
            battle = await self._battle_service.get_battle(battle_id)
            if not battle or battle.status == "finished":
                break

            result = await self._battle_service.process_ai_turn(battle_id)

            results.append(result)

            battle = await self._battle_service.get_battle(battle_id)
            if not battle or battle.status == "finished":
                break

        return results

    async def execute_next_turn(self, battle_id: str) -> dict[str, Any] | None:
        """Execute a single turn of an AI vs AI battle.

        Args:
            battle_id: ID of the battle.

        Returns:
            Turn result dict or None if battle is finished.
        """
        battle = await self._battle_service.get_battle(battle_id)
        if not battle or battle.status == "finished":
            return None

        result = await self._battle_service.process_ai_turn(battle_id)

        battle = await self._battle_service.get_battle(battle_id)
        return None if battle and battle.status == "finished" else result
