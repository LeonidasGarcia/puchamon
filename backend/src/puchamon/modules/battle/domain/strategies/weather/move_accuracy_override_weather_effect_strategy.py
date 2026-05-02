"""Strategy for `move_accuracy_override` weather effects."""

from .pending import PendingWeatherEffectStrategy


class MoveAccuracyOverrideWeatherEffectStrategy(PendingWeatherEffectStrategy):
    kind = "move_accuracy_override"
    hook = "modify_accuracy"
