"""Tests for battle stat resolution and damage calculation."""

from puchamon.modules.battle.domain import (
    DEFAULT_BATTLE_LEVEL,
    MAX_DAMAGE_ROLL_PERCENT,
    MIN_DAMAGE_ROLL_PERCENT,
    build_battle_stats,
)
from puchamon.modules.battle.domain.entities import Battle, BattleInstance, BattleStats, Player, SideState, StatStages
from puchamon.modules.battle.domain.mechanics import calculate_damage, resolve_damage_roll_percent
from puchamon.modules.battle.domain.runtime import BattleStrategyContext, MoveEffectExecutionInput
from puchamon.modules.battle.domain.strategies.effects.damage_effect_strategy import DamageEffectStrategy
from puchamon.modules.pokedex.domain.entities import MoveEffect, Movement, Moveset, Pokemon
from puchamon.modules.pokedex.domain.entities.effects import DamagePayload, RandomRange
from puchamon.modules.pokedex.domain.entities.pokemons import BaseStats


def _build_instance(
    *,
    instance_id: str,
    trainer_id: str,
    pokemon_id: str,
    types: list[str] | None = None,
    stats: BattleStats | None = None,
    level: int = DEFAULT_BATTLE_LEVEL,
    current_hp: int | None = None,
) -> BattleInstance:
    max_hp = stats.hp if stats is not None else 160
    resolved_current_hp = max_hp if current_hp is None else current_hp
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="battle-1",
        trainer_id=trainer_id,
        slot=0,
        pokemon_id=pokemon_id,
        moveset_id=f"moveset-{pokemon_id}",
        types=list(types or []),
        level=level,
        stats=stats,
        current_hp=resolved_current_hp,
        max_hp=max_hp,
        ability="pressure",
        item=None,
        status=None,
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=False,
        is_revealed=True,
        revealed_moves=[],
    )


def _build_pokemon(*, pokemon_id: str, types: list[str], hp: int, atk: int, defense: int, spa: int, spd: int, spe: int) -> Pokemon:
    return Pokemon.model_construct(
        id=pokemon_id,
        name=pokemon_id.capitalize(),
        types=types,
        base_stats=BaseStats(hp=hp, atk=atk, def_=defense, spa=spa, spd=spd, spe=spe),
        abilities=["pressure"],
    )


def _build_moveset(*, pokemon_id: str, nature: str = "Hardy", evs: dict[str, int] | None = None) -> Moveset:
    return Moveset.model_construct(
        id=f"moveset-{pokemon_id}",
        pokemon_id=pokemon_id,
        moveset_name=f"{pokemon_id}-set",
        nature=nature,
        evs=evs or {},
        item="leftovers",
        ability="pressure",
        moves=["tackle"],
    )


def _build_battle(*, source_instance_id: str, target_instance_id: str) -> Battle:
    return Battle.model_construct(
        id="battle-1",
        battle_type="1v1",
        turn=1,
        status="active",
        phase="resolving_turn",
        sides={
            "trainer-1": SideState(hazards=[], active_pokemon_instance_ids=[source_instance_id]),
            "trainer-2": SideState(hazards=[], active_pokemon_instance_ids=[target_instance_id]),
        },
        players=[
            Player(trainer_id="trainer-1", name="Ash", controller_type="human"),
            Player(trainer_id="trainer-2", name="Gary", controller_type="human"),
        ],
        current_turn_actions=[],
        result=None,
    )


def test_build_battle_stats_uses_nature_evs_iv31_and_level_100() -> None:
    pokemon = _build_pokemon(
        pokemon_id="dragonite",
        types=["dragon", "flying"],
        hp=100,
        atk=100,
        defense=100,
        spa=100,
        spd=100,
        spe=100,
    )
    moveset = _build_moveset(pokemon_id="dragonite", nature="Adamant", evs={"hp": 252, "atk": 252, "spe": 4})

    stats = build_battle_stats(pokemon=pokemon, moveset=moveset)

    assert stats.hp == 404
    assert stats.atk == 328
    assert stats.def_ == 236
    assert stats.spa == 212
    assert stats.spd == 236
    assert stats.spe == 237


def test_calculate_damage_applies_stab_and_deterministic_multi_hit() -> None:
    source_pokemon = _build_pokemon(
        pokemon_id="charizard",
        types=["fire", "flying"],
        hp=78,
        atk=100,
        defense=78,
        spa=109,
        spd=85,
        spe=100,
    )
    target_pokemon = _build_pokemon(
        pokemon_id="venusaur",
        types=["grass", "poison"],
        hp=80,
        atk=82,
        defense=100,
        spa=100,
        spd=100,
        spe=80,
    )
    source_moveset = _build_moveset(pokemon_id="charizard", evs={"atk": 252})
    target_moveset = _build_moveset(pokemon_id="venusaur")
    source_stats = build_battle_stats(pokemon=source_pokemon, moveset=source_moveset)
    target_stats = build_battle_stats(pokemon=target_pokemon, moveset=target_moveset)
    source_instance = _build_instance(
        instance_id="source-instance",
        trainer_id="trainer-1",
        pokemon_id="charizard",
        types=source_pokemon.types,
        stats=source_stats,
    )
    target_instance = _build_instance(
        instance_id="target-instance",
        trainer_id="trainer-2",
        pokemon_id="venusaur",
        types=target_pokemon.types,
        stats=target_stats,
    )
    movement = Movement.model_construct(
        id="fire-punch",
        name="Fire Punch",
        type="fire",
        category="physical",
        power=80,
        accuracy=100,
        pp=15,
        priority=0,
        target="target",
        makes_contact=True,
        protectable=True,
        effect_ids=[],
    )

    max_damage = calculate_damage(
        movement=movement,
        payload=DamagePayload(hits=RandomRange(mode="random_range", min=2, max=5)),
        source_instance=source_instance,
        target_instance=target_instance,
        damage_roll_percent=MAX_DAMAGE_ROLL_PERCENT,
        type_chart={},
    )
    min_damage = calculate_damage(
        movement=movement,
        payload=DamagePayload(hits=RandomRange(mode="random_range", min=2, max=5)),
        source_instance=source_instance,
        target_instance=target_instance,
        damage_roll_percent=MIN_DAMAGE_ROLL_PERCENT,
        type_chart={},
    )

    assert max_damage == 260
    assert min_damage == 220


def test_resolve_damage_roll_percent_uses_configured_value_or_rng(monkeypatch) -> None:
    monkeypatch.setattr("puchamon.modules.battle.domain.mechanics.damage.randint", lambda start, end: start)

    assert resolve_damage_roll_percent(MAX_DAMAGE_ROLL_PERCENT) == MAX_DAMAGE_ROLL_PERCENT
    assert resolve_damage_roll_percent() == MIN_DAMAGE_ROLL_PERCENT


def test_calculate_damage_respects_target_defense_override() -> None:
    source_pokemon = _build_pokemon(
        pokemon_id="alakazam",
        types=["psychic"],
        hp=55,
        atk=50,
        defense=45,
        spa=135,
        spd=95,
        spe=120,
    )
    target_pokemon = _build_pokemon(
        pokemon_id="snorlax",
        types=["normal"],
        hp=160,
        atk=110,
        defense=160,
        spa=65,
        spd=65,
        spe=30,
    )
    source_stats = build_battle_stats(pokemon=source_pokemon, moveset=_build_moveset(pokemon_id="alakazam", evs={"spa": 252}))
    target_stats = build_battle_stats(pokemon=target_pokemon, moveset=_build_moveset(pokemon_id="snorlax"))
    source_instance = _build_instance(
        instance_id="source-instance",
        trainer_id="trainer-1",
        pokemon_id="alakazam",
        types=source_pokemon.types,
        stats=source_stats,
    )
    target_instance = _build_instance(
        instance_id="target-instance",
        trainer_id="trainer-2",
        pokemon_id="snorlax",
        types=target_pokemon.types,
        stats=target_stats,
    )
    movement = Movement.model_construct(
        id="psyshock",
        name="Psyshock",
        type="psychic",
        category="special",
        power=80,
        accuracy=100,
        pp=10,
        priority=0,
        target="target",
        makes_contact=False,
        protectable=True,
        effect_ids=[],
    )

    regular_damage = calculate_damage(
        movement=movement,
        payload=DamagePayload(hits=1),
        source_instance=source_instance,
        target_instance=target_instance,
        damage_roll_percent=MAX_DAMAGE_ROLL_PERCENT,
        type_chart={},
    )
    override_damage = calculate_damage(
        movement=movement,
        payload=DamagePayload(hits=1, use_target_defense_stat="def"),
        source_instance=source_instance,
        target_instance=target_instance,
        damage_roll_percent=MAX_DAMAGE_ROLL_PERCENT,
        type_chart={},
    )

    assert regular_damage > override_damage


def test_damage_effect_strategy_uses_calculated_damage_from_instance_stats() -> None:
    source_pokemon = _build_pokemon(
        pokemon_id="pikachu",
        types=["electric"],
        hp=35,
        atk=110,
        defense=60,
        spa=50,
        spd=70,
        spe=90,
    )
    target_pokemon = _build_pokemon(
        pokemon_id="squirtle",
        types=["water"],
        hp=44,
        atk=48,
        defense=95,
        spa=50,
        spd=85,
        spe=43,
    )
    source_instance = _build_instance(
        instance_id="source-instance",
        trainer_id="trainer-1",
        pokemon_id="pikachu",
        types=source_pokemon.types,
        stats=build_battle_stats(pokemon=source_pokemon, moveset=_build_moveset(pokemon_id="pikachu", evs={"atk": 252})),
    )
    target_instance = _build_instance(
        instance_id="target-instance",
        trainer_id="trainer-2",
        pokemon_id="squirtle",
        types=target_pokemon.types,
        stats=build_battle_stats(pokemon=target_pokemon, moveset=_build_moveset(pokemon_id="squirtle")),
    )
    movement = Movement.model_construct(
        id="volt-tackle",
        name="Volt Tackle",
        type="electric",
        category="physical",
        power=90,
        accuracy=100,
        pp=15,
        priority=0,
        target="target",
        makes_contact=True,
        protectable=True,
        effect_ids=["effect-damage"],
    )
    payload = DamagePayload(hits=1)
    effect = MoveEffect.model_construct(id="effect-damage", kind="damage", target="target", chance=100, order=1, payload=payload)
    expected_damage = calculate_damage(
        movement=movement,
        payload=payload,
        source_instance=source_instance,
        target_instance=target_instance,
        damage_roll_percent=MAX_DAMAGE_ROLL_PERCENT,
        type_chart={},
    )
    context = BattleStrategyContext(
        battle=_build_battle(source_instance_id="source-instance", target_instance_id="target-instance"),
        battle_instances={
            "source-instance": source_instance,
            "target-instance": target_instance,
        },
    )
    execution = MoveEffectExecutionInput(
        effect=effect,
        source_instance_id="source-instance",
        target_instance_ids=["target-instance"],
        movement=movement,
        metadata={"damage_roll_percent": MAX_DAMAGE_ROLL_PERCENT},
    )

    DamageEffectStrategy().apply(context, execution)

    assert target_instance.current_hp == target_instance.max_hp - expected_damage
    assert context.events[-1].kind == "damage"
    assert context.events[-1].payload["damage_roll_percent"] == MAX_DAMAGE_ROLL_PERCENT
    assert context.events[-1].payload["value"] == expected_damage
