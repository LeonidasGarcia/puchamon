"""Mapper for battle turn DTOs."""

from ...domain.entities import Battle, BattleInstance, TurnAction
from ...domain.runtime.context import BattleStrategyContext, BattleStrategyEvent
from ..mappers.battle_snapshot_mapper import to_battle_snapshot_dto
from ..dto.battle_turn_dto import (
    BattleTurnDTO,
    BattleTurnEventDTO,
    DeclaredTurnActionDTO,
    ExecutedTurnActionDTO,
    ForcedReplacementDTO,
    TurnActionTargetDTO,
)


def to_turn_action_target_dto(target: "TurnAction | None") -> "TurnActionTargetDTO | None":
    """Map a TurnAction target to TurnActionTargetDTO."""
    if target is None:
        return None
    return TurnActionTargetDTO(
        scope=target.target.scope if target.target else "target",
        target_side=target.target.target_side if target.target else None,
        target_active_slot=target.target.target_active_slot if target.target else None,
    )


def to_declared_action_dto(action: TurnAction) -> DeclaredTurnActionDTO:
    """Map a TurnAction to DeclaredTurnActionDTO."""
    return DeclaredTurnActionDTO(
        trainer_id=action.player,
        action_type=action.type,
        user_instance_id=action.user_instance_id,
        move_id=action.move_id,
        target=to_turn_action_target_dto(action),
    )


def to_executed_action_dto(action: TurnAction, order: int) -> ExecutedTurnActionDTO:
    """Map a TurnAction to ExecutedTurnActionDTO with execution order."""
    return ExecutedTurnActionDTO(
        order=order,
        trainer_id=action.player,
        action_type=action.type,
        user_instance_id=action.user_instance_id,
        move_id=action.move_id,
        target=to_turn_action_target_dto(action),
        hit=None,
        skipped_reason=None,
        revealed_move=False,
    )


def to_battle_turn_event_dto(event: BattleStrategyEvent, order: int) -> BattleTurnEventDTO:
    """Map a BattleStrategyEvent to BattleTurnEventDTO."""
    return BattleTurnEventDTO(
        order=order,
        kind=event.kind,
        source_instance_id=event.source_instance_id,
        target_instance_id=event.target_instance_id,
        move_id=event.payload.get("move_id"),
        value=event.payload.get("value"),
        status_id=event.payload.get("status_id"),
        hazard_id=event.payload.get("hazard_id"),
        weather_id=event.payload.get("weather_id"),
        message=event.message,
    )


def detect_required_replacements(
    battle: Battle,
    battle_instances: dict[str, BattleInstance],
) -> list[ForcedReplacementDTO]:
    """Detect which slots need replacement after faints."""
    replacements: list[ForcedReplacementDTO] = []

    for trainer_id, side in battle.sides.items():
        active_ids = side.active_pokemon_instance_ids

        for slot_idx, instance_id in enumerate(active_ids):
            if instance_id is None:
                continue

            instance = battle_instances.get(instance_id)
            if instance is None:
                continue

            if instance.fainted:
                available_ids = [
                    inst.id
                    for inst in battle_instances.values()
                    if inst.trainer_id == trainer_id
                    and not inst.fainted
                    and inst.id not in active_ids
                ]
                available_ids = [uid for uid in available_ids if uid is not None]

                replacements.append(
                    ForcedReplacementDTO(
                        trainer_id=trainer_id,
                        active_slot=slot_idx,
                        fainted_instance_id=str(instance_id),
                        available_instance_ids=[str(uid) for uid in available_ids],
                    )
                )

    return replacements


def map_context_to_turn_dto(
    battle: Battle,
    declared_actions: list[TurnAction],
    executed_actions: list[TurnAction],
    context: BattleStrategyContext,
) -> BattleTurnDTO:
    """Map BattleStrategyContext and related data to BattleTurnDTO."""
    event_order = 0
    events: list[BattleTurnEventDTO] = []
    for event in context.events:
        events.append(to_battle_turn_event_dto(event, event_order))
        event_order += 1

    executed_dtos: list[ExecutedTurnActionDTO] = []
    for order, action in enumerate(executed_actions, start=1):
        executed_dtos.append(to_executed_action_dto(action, order))

    declared_dtos: list[DeclaredTurnActionDTO] = [
        to_declared_action_dto(action) for action in declared_actions
    ]

    return BattleTurnDTO(
        battle_id=str(battle.id),
        turn=battle.turn,
        declared_actions=declared_dtos,
        executed_actions=executed_dtos,
        events=events,
        fainted_instance_ids=context.get_fainted_instance_ids(),
        required_replacements=detect_required_replacements(
            battle, context.battle_instances
        ),
        post_turn_snapshot=to_battle_snapshot_dto(
            battle, list(context.battle_instances.values())
        ),
    )
