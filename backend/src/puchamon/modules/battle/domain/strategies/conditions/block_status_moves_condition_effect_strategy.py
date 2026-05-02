"""Strategy for `block_status_moves` condition effects."""

from .pending import PendingConditionEffectStrategy


class BlockStatusMovesConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "block_status_moves"
    hook = "validate_move"
