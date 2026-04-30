"""Concrete condition effect strategies keyed by `ConditionEffect.kind`."""

from .base import ConditionEffectStrategy
from ..context import BattleStrategyContext, ConditionEffectExecutionInput
from ...exceptions import BattleValidationError


class PendingConditionEffectStrategy(ConditionEffectStrategy):
    """Shared placeholder for condition effects that are not implemented yet."""

    kind: str
    hook: str

    def apply(self, context: BattleStrategyContext, execution: ConditionEffectExecutionInput) -> None:
        """Guard effect dispatch while the concrete logic is still pending."""
        if execution.effect.kind != self.kind:
            raise BattleValidationError(f"{self.__class__.__name__} cannot apply condition effect kind '{execution.effect.kind}'")

        raise NotImplementedError(f"Condition effect strategy '{self.kind}' is not implemented yet")


class EndTurnDamageConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "end_turn_damage"
    hook = "end_turn"


class BadPoisonConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "end_turn_bad_poison_damage"
    hook = "end_turn"


class PhysicalAttackModifierConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "physical_attack_modifier"
    hook = "modify_damage"


class SpeedModifierConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "speed_modifier"
    hook = "modify_speed"


class FullParalysisChanceConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "full_paralysis_chance"
    hook = "before_action"


class SelfHitChanceConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "self_hit_chance"
    hook = "before_action"


class CannotMoveConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "cannot_move"
    hook = "before_action"


class SkipActionConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "skip_action"
    hook = "before_action"


class BlockProtectableMovesConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "block_protectable_moves"
    hook = "validate_move"


class BlockStatusMovesConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "block_status_moves"
    hook = "validate_move"


class FaintOnExpireConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "faint_on_expire"
    hook = "on_expire"


class ProxyHpConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "proxy_hp"
    hook = "modify_damage"


class EndTurnDrainConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "end_turn_drain"
    hook = "end_turn"
