"""Strategy for `move_charge_modifier` weather effects."""

from .pending import PendingWeatherEffectStrategy


class MoveChargeModifierWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "move_charge_modifier"
    hook = "modify_charge"
