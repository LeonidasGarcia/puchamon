"""Strategy for `physical_attack_modifier` condition effects."""

from .pending import PendingConditionEffectStrategy


class PhysicalAttackModifierConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "physical_attack_modifier"
    hook = "modify_damage"
