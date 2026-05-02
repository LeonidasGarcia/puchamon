"""Strategy for `swap_item` move effects."""

from .pending import PendingMoveEffectStrategy


class SwapItemEffectStrategy(PendingMoveEffectStrategy):
    kind = "swap_item"
