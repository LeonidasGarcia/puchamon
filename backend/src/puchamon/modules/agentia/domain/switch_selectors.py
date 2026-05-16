"""Switch selection strategies for AI."""

import random
from abc import ABC, abstractmethod

from ...battle.domain.entities import Battle, BattleInstance


class SwitchSelector(ABC):
    """Abstract base class for switch selection strategies."""

    @abstractmethod
    def select(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
    ) -> str | None:
        """Select a replacement Pokemon to switch in.

        Args:
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            trainer_id: ID of the trainer making the switch.

        Returns:
            The replacement instance_id or None if no replacement available.
        """
        pass


class RandomSwitchSelector(SwitchSelector):
    """Select a replacement randomly (Level 1 - Easy)."""

    def select(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
    ) -> str | None:
        """Select a random replacement Pokemon.

        Args:
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            trainer_id: ID of the trainer making the switch.

        Returns:
            A random replacement instance_id or None if no replacement available.
        """
        side = battle.sides.get(trainer_id)
        if not side:
            return None

        active_ids: set[str] = {uid for uid in side.active_pokemon_instance_ids if uid is not None}

        available_replacements: list[BattleInstance] = [
            inst for inst in instances.values() if inst.trainer_id == trainer_id and not inst.fainted and inst.id not in active_ids
        ]

        if not available_replacements:
            return None

        replacement: BattleInstance = random.choice(available_replacements)
        return str(replacement.id)


class BestHPSwitchSelector(SwitchSelector):
    """Select replacement with highest HP percentage (Level 2+)."""

    def select(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
    ) -> str | None:
        """Select replacement with highest HP%.

        Args:
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            trainer_id: ID of the trainer making the switch.

        Returns:
            The replacement instance_id with highest HP% or None if no replacement available.
        """
        side = battle.sides.get(trainer_id)
        if not side:
            return None

        active_ids: set[str] = {uid for uid in side.active_pokemon_instance_ids if uid is not None}

        available_replacements: list[BattleInstance] = [
            inst for inst in instances.values() if inst.trainer_id == trainer_id and not inst.fainted and inst.id not in active_ids
        ]

        if not available_replacements:
            return None

        def get_hp_percent(inst: BattleInstance) -> float:
            return inst.current_hp / inst.max_hp if inst.max_hp > 0 else 0.0

        replacement: BattleInstance = max(available_replacements, key=get_hp_percent)
        return str(replacement.id)
