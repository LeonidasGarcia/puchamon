"""Concrete move effect strategy declarations keyed by `MoveEffect.kind`."""

from .base import MoveEffectStrategy
from ..context import BattleStrategyContext, MoveEffectExecutionInput
from ...exceptions import BattleValidationError


class PendingMoveEffectStrategy(MoveEffectStrategy):
    """Shared placeholder for move effect kinds that are not implemented yet."""

    kind: str

    def apply(self, context: BattleStrategyContext, execution: MoveEffectExecutionInput) -> None:
        """Guard effect dispatch while the concrete logic is still pending."""
        if execution.effect.kind != self.kind:
            raise BattleValidationError(f"{self.__class__.__name__} cannot apply move effect kind '{execution.effect.kind}'")

        raise NotImplementedError(f"Move effect strategy '{self.kind}' is not implemented yet")


class DamageEffectStrategy(PendingMoveEffectStrategy):
    kind = "damage"


class ApplyMajorStatusEffectStrategy(PendingMoveEffectStrategy):
    kind = "apply_major_status"


class ApplyVolatileStatusEffectStrategy(PendingMoveEffectStrategy):
    kind = "apply_volatile_status"


class ModifyStatEffectStrategy(PendingMoveEffectStrategy):
    kind = "modify_stat"


class SetHazardEffectStrategy(PendingMoveEffectStrategy):
    kind = "set_hazard"


class RemoveHazardEffectStrategy(PendingMoveEffectStrategy):
    kind = "remove_hazard"


class ProtectEffectStrategy(PendingMoveEffectStrategy):
    kind = "protect"


class HealHpEffectStrategy(PendingMoveEffectStrategy):
    kind = "heal_hp"


class SelfSwitchEffectStrategy(PendingMoveEffectStrategy):
    kind = "self_switch"


class SwapItemEffectStrategy(PendingMoveEffectStrategy):
    kind = "swap_item"


class PainSplitEffectStrategy(PendingMoveEffectStrategy):
    kind = "pain_split"
