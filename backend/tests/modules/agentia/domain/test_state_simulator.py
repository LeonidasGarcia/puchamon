"""Tests for AI state simulation."""

from puchamon.modules.agentia.domain.state_simulator import simulate_state_transition
from puchamon.modules.battle.domain.entities import Battle, BattleInstance, BattleStats, MoveState, SideState, StatStages
from puchamon.modules.pokedex.domain.entities import MoveEffect, Movement
from puchamon.modules.pokedex.domain.entities.effects import ModifyStatPayload, StatChange


def make_instance(instance_id: str, trainer_id: str, move_id: str | None = None) -> BattleInstance:
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=0,
        pokemon_id="test-pokemon",
        moveset_id="ms1",
        types=["Normal"],
        level=50,
        stats=BattleStats(hp=100, atk=100, def_=100, spa=100, spd=100, spe=100),
        current_hp=100,
        max_hp=100,
        ability="test-ability",
        status=None,
        volatile_status=[],
        stages=StatStages(),
        move_state=[MoveState(move_id=move_id, current_pp=10)] if move_id else [],
        fainted=False,
        is_revealed=True,
        revealed_moves=[],
    )


def make_battle() -> Battle:
    return Battle.model_construct(
        id="b1",
        battle_type="1v1",
        turn=1,
        status="active",
        phase="awaiting_actions",
        sides={
            "player": SideState(active_pokemon_instance_ids=["p1"]),
            "opponent": SideState(active_pokemon_instance_ids=["p2"]),
        },
        players=[],
        current_turn_actions=[],
    )


def test_simulates_guaranteed_self_stat_drop() -> None:
    move = Movement.model_construct(
        id="self-drop",
        name="Self Drop",
        type="Normal",
        category="Special",
        power=1,
        accuracy=100,
        pp=10,
        priority=0,
        target="target",
        makes_contact=False,
        protectable=True,
        effect_ids=["self-drop-effect"],
    )
    effect = MoveEffect.model_construct(
        id="self-drop-effect",
        kind="modify_stat",
        target="self",
        chance=100,
        order=1,
        payload=ModifyStatPayload(changes=[StatChange(stat="spa", stages=-2)]),
    )

    _, instances = simulate_state_transition(
        make_battle(),
        {"p1": make_instance("p1", "player", "self-drop"), "p2": make_instance("p2", "opponent")},
        ("MOVE", "self-drop"),
        "player",
        "opponent",
        movements={"self-drop": move},
        move_effects={"self-drop-effect": effect},
    )

    assert instances["p1"].stages.spa == -2
