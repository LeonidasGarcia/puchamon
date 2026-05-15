"""Battlefield targeting and side resolution helpers."""

from beanie import PydanticObjectId

from ....pokedex.domain.entities import MoveEffect
from ..entities import Battle, BattleInstance, SideState, TargetScope
from ..exceptions import BattleValidationError


def _require_instance_id(instance_id: str | PydanticObjectId | None) -> str:
    """Normalize battle instance identifiers when Beanie injects ObjectId types."""
    if instance_id is None:
        raise BattleValidationError("Battle instances must have an id before resolving battlefield targets")
    return str(instance_id)


def _list_active_instance_ids(side: SideState) -> list[str]:
    """Return the non-empty active battlefield occupants for a side."""
    return [instance_id for instance_id in side.active_pokemon_instance_ids if instance_id is not None]


def _list_all_active_instance_ids(*sides: SideState) -> list[str]:
    """Return the non-empty active battlefield occupants across multiple sides."""
    active_instance_ids: list[str] = []
    for side in sides:
        active_instance_ids.extend(_list_active_instance_ids(side))
    return active_instance_ids


def get_side_for_trainer(battle: Battle, trainer_id: str) -> SideState:
    """Return the side state for a trainer participating in the battle."""
    try:
        return battle.sides[trainer_id]
    except KeyError as exc:
        raise BattleValidationError(f"Trainer '{trainer_id}' is not registered in the current battle sides") from exc


def get_opponent_trainer_id(battle: Battle, trainer_id: str) -> str:
    """Return the opposing trainer identifier for two-sided battles."""
    for player in battle.players:
        if player.trainer_id != trainer_id:
            return player.trainer_id
    raise BattleValidationError(f"Could not resolve an opponent side for trainer '{trainer_id}'")


def get_active_slot_for_instance(side: SideState, instance_id: str) -> int:
    """Return the active battlefield slot occupied by a given instance."""
    try:
        return side.active_pokemon_instance_ids.index(instance_id)
    except ValueError as exc:
        raise BattleValidationError(f"Battle instance '{instance_id}' is not currently active on the expected side") from exc


def set_active_instance_for_slot(side: SideState, active_slot: int, instance_id: str | None) -> None:
    """Replace the instance occupying a given active slot."""
    if active_slot < 0 or active_slot >= len(side.active_pokemon_instance_ids):
        raise BattleValidationError(f"Active slot '{active_slot}' is outside the current battlefield range")
    side.active_pokemon_instance_ids[active_slot] = instance_id


def get_active_instance_id_for_target(battle: Battle, source_trainer_id: str, target: TargetScope) -> str | None:
    """Resolve the current occupant of a target battlefield slot."""
    if target.target_side is None or target.target_active_slot is None:
        raise BattleValidationError("Targeted actions must provide both target_side and target_active_slot")

    target_trainer_id = source_trainer_id if target.target_side == "ally_side" else get_opponent_trainer_id(battle, source_trainer_id)
    side: SideState = get_side_for_trainer(battle, target_trainer_id)

    if target.target_active_slot < 0 or target.target_active_slot >= len(side.active_pokemon_instance_ids):
        raise BattleValidationError(f"Target active slot '{target.target_active_slot}' is outside the current battlefield range")

    return side.active_pokemon_instance_ids[target.target_active_slot]


def resolve_effect_target_instance_ids(
    battle: Battle,
    source_instance: BattleInstance,
    action_target: TargetScope | None,
    effect: MoveEffect,
) -> list[str]:
    """Resolve target instance identifiers for a move effect against the current battlefield state."""
    source_side: SideState = get_side_for_trainer(battle, source_instance.trainer_id)
    opponent_side: SideState = get_side_for_trainer(battle, get_opponent_trainer_id(battle, source_instance.trainer_id))
    target_instance_ids: list[str]

    if effect.target in {"self", "user"}:
        target_instance_ids = [_require_instance_id(source_instance.id)]
    elif effect.target in {"foe_side", "opponent_side"}:
        target_instance_ids = _list_active_instance_ids(opponent_side)
    elif effect.target in {"ally_side", "user_side"}:
        target_instance_ids = _list_active_instance_ids(source_side)
    elif effect.target in {"field", "all_sides"}:
        target_instance_ids = _list_all_active_instance_ids(source_side, opponent_side)
    else:
        if action_target is None:
            raise BattleValidationError("Targeted move effects require an action target to be resolved")

        if action_target.scope in {"self", "user"}:
            target_instance_ids = [_require_instance_id(source_instance.id)]
        elif action_target.scope == "target":
            target_instance_id: str | None = get_active_instance_id_for_target(battle, source_instance.trainer_id, action_target)
            target_instance_ids = [target_instance_id] if target_instance_id is not None else []
        elif action_target.scope in {"all", "all_sides"}:
            target_instance_ids = _list_all_active_instance_ids(source_side, opponent_side)
        else:
            raise BattleValidationError(f"Target scope '{action_target.scope}' is not supported for move effect resolution yet")

    return target_instance_ids
