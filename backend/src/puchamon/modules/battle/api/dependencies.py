"""Dependency injection for battle API."""

from ...agentia.application.services.ia_service import IAService
from ..application.services.battle_coordinator_service import BattleCoordinatorService
from ..application.services.battle_service import BattleService


def get_battle_service() -> BattleService:
    """Provide a battle service instance for dependency injection.

    This function creates and returns a new BattleService to be used by API endpoints.

    Returns:
        BattleService: A new instance of the battle service.
    """
    return BattleService()


def get_ia_service() -> IAService:
    """Provide an IA service instance for dependency injection.

    This function creates and returns a new IAService to be used by API endpoints.

    Returns:
        IAService: A new instance of the IA service.
    """
    return IAService()


def get_battle_coordinator_service() -> BattleCoordinatorService:
    """Provide a BattleCoordinatorService instance for battles.

    Wires up the required BattleService and IAService.
    """
    return BattleCoordinatorService(
        battle_service=get_battle_service(),
        ia_service=get_ia_service(),
    )
