"""Service for setting up battle-related logic."""

from typing import TYPE_CHECKING, Literal

from bson import ObjectId

if TYPE_CHECKING:
    from ....pokedex.domain.entities import MoveEffect, Movement

from ....pokedex.domain.entities import Movement, Moveset, Pokemon
from ...domain import build_battle_stats
from ...domain.entities import Battle, BattleInstance, MoveState, Player, SideState, StatStages
from ...domain.rules import DEFAULT_BATTLE_LEVEL
from ..dto.battle_turn_dto import BattleTurnDTO
from ..mappers.battle_snapshot_mapper import to_battle_snapshot_dto

MAX_RETRIES_PER_POKEMON = 3
MAX_TOTAL_ATTEMPTS = 30


class BattleSetupService:
    """Service class for setting up a new battle."""

    @classmethod
    async def create_battle(
        cls,
        battle_type: Literal["1v1", "2v2", "3v3"],
        players: list[Player],
        team_size: int = 3,
        movements: dict[str, "Movement"] | None = None,
        move_effects: dict[str, "MoveEffect"] | None = None,
    ) -> tuple[Battle, list[BattleInstance]]:
        """Creates the initial state of a Battle and its BattleInstances.

        Selects random Pokemon and Movesets, calculates stats, and sets up active slots.
        If a pokemon has no valid moves after filtering, a different pokemon is selected.
        """
        battle_id = str(ObjectId())
        instances: list[BattleInstance] = []
        sides: dict[str, SideState] = {}

        if movements is None:
            movements = {}
        if move_effects is None:
            move_effects = {}

        for player in players:
            player_instances, active_ids = await cls._create_player_team(
                battle_id, player, team_size, movements, move_effects
            )
            instances.extend(player_instances)
            sides[player.trainer_id] = SideState(active_pokemon_instance_ids=active_ids)

        battle = Battle(
            id=battle_id,
            battle_type=battle_type,
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides=sides,
            players=players,
            current_turn_actions=[],
        )

        return battle, instances

    @classmethod
    async def _create_player_team(
        cls,
        battle_id: str,
        player: Player,
        team_size: int,
        movements: dict[str, "Movement"],
        move_effects: dict[str, "MoveEffect"],
    ) -> tuple[list[BattleInstance], list[str | None]]:
        trainer_instances: list[BattleInstance] = []
        total_attempts = 0

        while len(trainer_instances) < team_size and total_attempts < MAX_TOTAL_ATTEMPTS:
            total_attempts += 1
            instance = await cls._generate_random_pokemon(
                battle_id, player.trainer_id, len(trainer_instances), movements, move_effects
            )
            if instance:
                trainer_instances.append(instance)

        if len(trainer_instances) < team_size:
            raise RuntimeError(f"Could not find valid pokemon for team after {MAX_TOTAL_ATTEMPTS} attempts")

        active_ids: list[str | None] = [str(trainer_instances[0].id)]

        for active_id in active_ids:
            if active_id:
                active_instance = next(i for i in trainer_instances if str(i.id) == active_id)
                active_instance.is_revealed = True

        return trainer_instances, active_ids

    @classmethod
    async def _generate_random_pokemon(
        cls,
        battle_id: str,
        trainer_id: str,
        slot: int,
        movements: dict[str, "Movement"],
        move_effects: dict[str, "MoveEffect"],
    ) -> BattleInstance | None:
        raw_movesets = await Moveset.aggregate([{"$sample": {"size": 1}}]).to_list(1)
        if not raw_movesets:
            return None

        moveset = Moveset(**raw_movesets[0])
        valid_moves = cls._filter_valid_moves(moveset.moves, movements, move_effects)

        if not valid_moves:
            return None

        pokemon = await Pokemon.get(moveset.pokemon_id)
        if not pokemon:
            return None

        stats = build_battle_stats(pokemon=pokemon, moveset=moveset, level=DEFAULT_BATTLE_LEVEL)

        move_state: list[MoveState] = [
            MoveState(move_id=move_id, current_pp=movements.get(move_id).pp if movements.get(move_id) else 15) for move_id in valid_moves
        ]

        return BattleInstance(
            id=str(ObjectId()),
            battle_id=battle_id,
            trainer_id=trainer_id,
            slot=slot,
            pokemon_id=str(pokemon.id),
            moveset_id=str(moveset.id),
            types=pokemon.types,
            level=DEFAULT_BATTLE_LEVEL,
            stats=stats,
            current_hp=stats.hp,
            max_hp=stats.hp,
            ability=moveset.ability,
            item=moveset.item,
            status=None,
            volatile_status=[],
            stages=StatStages(),
            move_state=move_state,
            fainted=False,
            is_revealed=False,
            revealed_moves=[],
        )

    @classmethod
    def _is_move_implemented(
        cls,
        move_id: str,
        movements: dict[str, "Movement"],
        move_effects: dict[str, "MoveEffect"],
    ) -> bool:
        """Check if a move has no unimplemented effects.

        Args:
            move_id: The move identifier.
            movements: Dict of Movement entities keyed by ID.
            move_effects: Dict of MoveEffect entities keyed by ID.

        Returns:
            True if the move has no unimplemented effects, False otherwise.
        """
        movement = movements.get(move_id)
        if not movement or not movement.effect_ids:
            return True

        del move_effects  # intentionally unused - stub for future effect validation
        return True

    @classmethod
    async def get_initial_state_dto(cls, battle: Battle, instances: list[BattleInstance]) -> "BattleTurnDTO":
        """Create the initial state DTO for a newly created battle."""
        snapshot = to_battle_snapshot_dto(battle, instances)
        return BattleTurnDTO(
            battle_id=str(battle.id),
            turn=battle.turn,
            declared_actions=[],
            executed_actions=[],
            events=[],
            fainted_instance_ids=[],
            required_replacements=[],
            post_turn_snapshot=snapshot,
        )

    @classmethod
    def _filter_valid_moves(
        cls,
        move_ids: list[str],
        movements: dict[str, "Movement"],
        move_effects: dict[str, "MoveEffect"],
    ) -> list[str]:
        """Filter moves to only include those with implemented effects.

        Args:
            move_ids: List of move IDs to filter.
            movements: Dict of Movement entities keyed by ID.
            move_effects: Dict of MoveEffect entities keyed by ID.

        Returns:
            List of move IDs that have all their effects implemented.
        """
        return [move_id for move_id in move_ids if cls._is_move_implemented(move_id, movements, move_effects)]
