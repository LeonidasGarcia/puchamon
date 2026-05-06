"""Service for setting up battle-related logic."""

from typing import Literal

from bson import ObjectId

from ....pokedex.domain.entities import Movement, Moveset, Pokemon
from ...domain import build_battle_stats
from ...domain.entities import Battle, BattleInstance, MoveState, Player, SideState, StatStages
from ...domain.rules import DEFAULT_BATTLE_LEVEL


class BattleSetupService:
    """Service class for setting up a new battle."""

    @classmethod
    async def create_battle(
        cls,
        battle_type: Literal["1v1", "2v2", "3v3"],
        players: list[Player],
        team_size: int = 3,
    ) -> tuple[Battle, list[BattleInstance]]:
        """Creates the initial state of a Battle and its BattleInstances.

        Selects random Pokemon and Movesets, calculates stats, and sets up active slots.
        """
        battle_id = str(ObjectId())
        instances: list[BattleInstance] = []
        sides: dict[str, SideState] = {}

        # Determine number of active slots based on battle_type
        active_slots = int(battle_type[0])  # "1v1" -> 1, "2v2" -> 2

        for player in players:
            # Randomly select 'team_size' movesets from the DB
            # We sample movesets first to ensure the selected pokemon actually has a valid moveset
            # Note: Beanie's aggregate returns raw dicts, we need to convert them to models
            raw_movesets = await Moveset.aggregate([{"$sample": {"size": team_size}}]).to_list(team_size)
            random_movesets: list[Moveset] = [Moveset(**m) for m in raw_movesets]

            trainer_instances: list[BattleInstance] = []

            for idx, moveset in enumerate(random_movesets):
                # Fetch the corresponding Pokemon
                pokemon = await Pokemon.get(moveset.pokemon_id)
                if not pokemon:
                    continue  # Should not happen if DB is consistent

                # Build stats using the isolated mechanics
                stats = build_battle_stats(pokemon=pokemon, moveset=moveset, level=DEFAULT_BATTLE_LEVEL)

                # Fetch moves to get correct PP
                move_state: list[MoveState] = []
                for move_id in moveset.moves:
                    movement = await Movement.get(move_id)
                    max_pp = movement.pp if movement else 15
                    move_state.append(MoveState(move_id=move_id, current_pp=max_pp))

                instance = BattleInstance(
                    id=str(ObjectId()),
                    battle_id=battle_id,
                    trainer_id=player.trainer_id,
                    slot=idx,
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
                trainer_instances.append(instance)

            instances.extend(trainer_instances)

            # Setup active slots (e.g. the first N pokemon are active)
            active_ids: list[str | None] = [str(trainer_instances[i].id) if i < len(trainer_instances) else None for i in range(active_slots)]

            sides[player.trainer_id] = SideState(hazards=[], active_pokemon_instance_ids=active_ids)

            # Reveal the active ones
            for active_id in active_ids:
                if active_id:
                    active_instance = next(i for i in trainer_instances if str(i.id) == active_id)
                    active_instance.is_revealed = True

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
