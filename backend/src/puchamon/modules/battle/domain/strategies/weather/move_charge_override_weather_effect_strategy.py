"""Strategy for `move_charge_override` weather effects."""

from .pending import PendingWeatherEffectStrategy


class MoveChargeOverrideWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "move_charge_override"
    hook = "modify_charge"
