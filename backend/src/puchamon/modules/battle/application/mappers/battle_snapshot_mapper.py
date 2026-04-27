"""Mappers for battle snapshot DTOs."""

from beanie import PydanticObjectId

from ...domain.entities import Battle, BattleInstance
from ...domain.entities.battle import BattleResult, Player, SideState, WeatherState
from ...domain.entities.battle_instance import MoveState, StatStages
from ..dto import (
    BattleResultDTO,
    BattleSnapshotDTO,
    MoveStateSnapshotDTO,
    PlayerSnapshotDTO,
    PokemonInstanceSnapshotDTO,
    SideSnapshotDTO,
    StatStagesSnapshotDTO,
    WeatherSnapshotDTO,
)


def _require_id(entity_id: str | PydanticObjectId | None, entity_name: str) -> str:
    """Ensure persisted entities expose an ID before leaving the application layer."""
    if entity_id is None:
        raise ValueError(f"{entity_name} must have an id before mapping to a DTO")
    return str(object=entity_id)


def to_weather_snapshot_dto(weather: WeatherState) -> WeatherSnapshotDTO:
    """Map a battle weather state into a snapshot DTO."""
    return WeatherSnapshotDTO(
        weather_id=weather.weather_id,
        remaining_turns=weather.remaining_turns,
        source_move_id=weather.source_move_id,
    )


def to_player_snapshot_dto(player: Player) -> PlayerSnapshotDTO:
    """Map a battle player into a snapshot DTO."""
    return PlayerSnapshotDTO(
        trainer_id=player.trainer_id,
        name=player.name,
        controller_type=player.controller_type,
    )


def to_side_snapshot_dto(side: SideState) -> SideSnapshotDTO:
    """Map a side state into a snapshot DTO."""
    return SideSnapshotDTO(
        hazards=side.hazards,
        active_pokemon_instance_ids=side.active_pokemon_instance_ids,
    )


def to_move_state_snapshot_dto(move_state: MoveState) -> MoveStateSnapshotDTO:
    """Map a move state into a snapshot DTO."""
    return MoveStateSnapshotDTO(
        move_id=move_state.move_id,
        current_pp=move_state.current_pp,
    )


def to_stat_stages_snapshot_dto(stages: StatStages) -> StatStagesSnapshotDTO:
    """Map stat stages into a snapshot DTO."""
    return StatStagesSnapshotDTO(
        atk=stages.atk,
        def_=stages.def_,
        spa=stages.spa,
        spd=stages.spd,
        spe=stages.spe,
        acc=stages.acc,
        eva=stages.eva,
    )


def to_pokemon_instance_snapshot_dto(battle_instance: BattleInstance) -> PokemonInstanceSnapshotDTO:
    """Map a battle instance into a snapshot DTO."""
    return PokemonInstanceSnapshotDTO(
        instance_id=_require_id(battle_instance.id, "BattleInstance"),
        trainer_id=battle_instance.trainer_id,
        team_slot=battle_instance.slot,
        pokemon_id=battle_instance.pokemon_id,
        level=battle_instance.level,
        current_hp=battle_instance.current_hp,
        max_hp=battle_instance.max_hp,
        status=battle_instance.status,
        volatile_status=battle_instance.volatile_status,
        stages=to_stat_stages_snapshot_dto(battle_instance.stages),
        move_state=[to_move_state_snapshot_dto(move_state) for move_state in battle_instance.move_state],
        fainted=battle_instance.fainted,
        is_revealed=battle_instance.is_revealed,
        revealed_moves=battle_instance.revealed_moves,
    )


def to_battle_result_dto(result: BattleResult) -> BattleResultDTO:
    """Map a finished battle result into a DTO."""
    return BattleResultDTO(
        winner_trainer_id=result.winner_trainer_id,
        reason=result.reason,
    )


def to_battle_snapshot_dto(battle: Battle, battle_instances: list[BattleInstance]) -> BattleSnapshotDTO:
    """Map a battle aggregate into its snapshot DTO."""
    return BattleSnapshotDTO(
        battle_id=_require_id(battle.id, "Battle"),
        battle_type=battle.battle_type,
        turn=battle.turn,
        status=battle.status,
        phase=battle.phase,
        weather=to_weather_snapshot_dto(battle.weather) if battle.weather else None,
        players=[to_player_snapshot_dto(player) for player in battle.players],
        sides={trainer_id: to_side_snapshot_dto(side) for trainer_id, side in battle.sides.items()},
        pokemon_instances=[to_pokemon_instance_snapshot_dto(instance) for instance in battle_instances],
        result=to_battle_result_dto(battle.result) if battle.result else None,
    )
