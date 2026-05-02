"""Strategy for `block_protectable_moves` condition effects."""

from .pending import PendingConditionEffectStrategy


class BlockProtectableMovesConditionEffectStrategy(PendingConditionEffectStrategy):
    kind = "block_protectable_moves"
    hook = "validate_move"
