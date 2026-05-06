"""Service for handling battle-related logic and lifecycle."""


from ...domain.entities import Battle, TurnAction
from .turn_resolution_service import TurnResolutionService


class BattleService:
    """Application service that acts as the entry point for Battle use cases.

    It orchestrates the flow between the database, setup, and turn resolution.
    """

    def __init__(self, turn_resolution_service: TurnResolutionService) -> None:
        self._turn_resolution = turn_resolution_service

    async def get_battle(self, battle_id: str) -> Battle:
        """Retrieves a battle from the database."""
        pass

    async def submit_action(self, battle_id: str, player_id: str, action: TurnAction) -> Battle:
        """Receives an action from a player (REST or WebSocket).

        If all players have submitted their actions, it triggers the TurnResolutionService
        to execute the turn, saves the new state to the DB, and returns the result.
        """
        pass

    async def forfeit_battle(self, battle_id: str, player_id: str) -> Battle:
        """Ends the battle immediately because a player surrendered."""
        pass
