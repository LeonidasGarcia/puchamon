"""Tests for AI heuristic functions."""

from puchamon.modules.agentia.domain.heuristics import (
    evaluate_level_2,
    evaluate_level_3_ga,
    evaluate_level_3_manual,
    evaluate_level_3_weighted,
    get_hp_percent,
)
from puchamon.modules.battle.domain.entities import Battle, BattleInstance, SideState, StatStages, BattleStats, MoveState
from puchamon.modules.pokedex.domain.entities import MoveEffect, Movement
from puchamon.modules.pokedex.domain.entities.effects import ModifyStatPayload, StatChange


def make_instance(instance_id, trainer_id, current_hp, max_hp, fainted=False, status=None):
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=0,
        pokemon_id="TestPokemon",
        moveset_id="ms1",
        types=["Normal"],
        level=50,
        stats=BattleStats(hp=100, atk=100, def_=100, spa=100, spd=100, spe=100),
        current_hp=current_hp,
        max_hp=max_hp,
        ability="TestAbility",
        status=status,
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=fainted,
        is_revealed=True,
        revealed_moves=[],
    )


def make_battle():
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


def make_status_move(move_id, effect_id):
    return Movement.model_construct(
        id=move_id,
        name=move_id,
        type="Normal",
        category="Status",
        power=None,
        accuracy=100,
        pp=10,
        priority=0,
        target="self",
        makes_contact=False,
        protectable=True,
        effect_ids=[effect_id],
    )


def make_stat_effect(effect_id, target, stat, stages):
    return MoveEffect.model_construct(
        id=effect_id,
        kind="modify_stat",
        target=target,
        chance=100,
        order=1,
        payload=ModifyStatPayload(changes=[StatChange(stat=stat, stages=stages)]),
    )


class TestGetHpPercent:
    """Tests for get_hp_percent function."""

    def test_full_hp_returns_one(self):
        instance = make_instance("p1", "t1", 100, 100)
        assert get_hp_percent(instance) == 1.0

    def test_half_hp_returns_point_five(self):
        instance = make_instance("p1", "t1", 50, 100)
        assert get_hp_percent(instance) == 0.5

    def test_empty_hp_returns_zero(self):
        instance = make_instance("p1", "t1", 0, 100)
        assert get_hp_percent(instance) == 0.0

    def test_fainted_returns_zero(self):
        instance = make_instance("p1", "t1", 50, 100, fainted=True)
        assert get_hp_percent(instance) == 0.0

    def test_over_max_hp_clamped_to_one(self):
        instance = make_instance("p1", "t1", 150, 100)
        assert get_hp_percent(instance) == 1.0

    def test_negative_hp_returns_zero(self):
        instance = make_instance("p1", "t1", -10, 100)
        assert get_hp_percent(instance) == 0.0


class TestEvaluateLevel2:
    """Tests for evaluate_level_2 heuristic function."""

    def test_equal_hp_returns_zero(self):
        p1 = make_instance("p1", "player", 50, 100)
        p2 = make_instance("p2", "opponent", 50, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_2(battle, instances, "player")

        assert score == 0.0

    def test_player_advantage_returns_positive(self):
        p1 = make_instance("p1", "player", 80, 100)
        p2 = make_instance("p2", "opponent", 20, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_2(battle, instances, "player")

        assert 0.55 < score <= 1.0

    def test_opponent_advantage_returns_negative(self):
        p1 = make_instance("p1", "player", 20, 100)
        p2 = make_instance("p2", "opponent", 80, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_2(battle, instances, "player")

        assert -1.0 <= score < -0.55

    def test_clamped_to_plus_one(self):
        p1 = make_instance("p1", "player", 100, 100)
        p2 = make_instance("p2", "opponent", 0, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_2(battle, instances, "player")

        assert score == 1.0

    def test_clamped_to_minus_one(self):
        p1 = make_instance("p1", "player", 0, 100)
        p2 = make_instance("p2", "opponent", 100, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_2(battle, instances, "player")

        assert score == -1.0


class TestEvaluateLevel3:
    """Tests for level 3 heuristic functions."""

    def test_equal_state_returns_near_zero(self):
        p1 = make_instance("p1", "player", 50, 100)
        p2 = make_instance("p2", "opponent", 50, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_3_manual(battle, instances, "player")

        assert -0.2 < score < 0.2

    def test_player_status_penalty_decreases_score(self):
        p1 = make_instance("p1", "player", 50, 100, status="burn")
        p2 = make_instance("p2", "opponent", 50, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_3_manual(battle, instances, "player")

        assert score < 0.0

    def test_opponent_status_penalty_increases_score(self):
        p1 = make_instance("p1", "player", 50, 100)
        p2 = make_instance("p2", "opponent", 50, 100, status="poison")

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_3_manual(battle, instances, "player")

        assert score > 0.0

    def test_moreAlive_pokemon_increases_score(self):
        p1 = make_instance("p1", "player", 50, 100)
        p2 = make_instance("p2", "player", 50, 100)
        p3 = make_instance("p3", "player", 50, 100)
        p4 = make_instance("p4", "opponent", 50, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "player": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p4"]),
            },
            players=[],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2, "p3": p3, "p4": p4}

        score = evaluate_level_3_manual(battle, instances, "player")

        assert score > 0.0

    def test_score_uses_ga_optimized_scale(self):
        p1 = make_instance("p1", "player", 100, 100)
        p2 = make_instance("p2", "opponent", 0, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        score = evaluate_level_3_ga(battle, instances, "player")

        assert 0.0 < score <= 1.0

    def test_manual_and_ga_weights_are_distinct(self):
        p1 = make_instance("p1", "player", 100, 100)
        p2 = make_instance("p2", "opponent", 25, 100)

        battle = Battle.model_construct(
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
        instances = {"p1": p1, "p2": p2}

        manual_score = evaluate_level_3_manual(battle, instances, "player")
        ga_score = evaluate_level_3_ga(battle, instances, "player")

        assert manual_score != ga_score

    def test_self_negative_stat_effect_decreases_effect_score(self):
        p1 = make_instance("p1", "player", 50, 100)
        p2 = make_instance("p2", "opponent", 50, 100)
        p1.move_state = [MoveState(move_id="self-drop", current_pp=10)]
        move = make_status_move("self-drop", "self-drop-effect")
        move.power = 1
        battle = make_battle()

        score = evaluate_level_3_weighted(
            battle,
            {"p1": p1, "p2": p2},
            "player",
            movements={"self-drop": move},
            move_effects={"self-drop-effect": make_stat_effect("self-drop-effect", "self", "spa", -2)},
            weights={"effects": 1.0},
        )

        assert score < 0.0

    def test_target_negative_stat_effect_increases_effect_score(self):
        p1 = make_instance("p1", "player", 50, 100)
        p2 = make_instance("p2", "opponent", 50, 100)
        p1.move_state = [MoveState(move_id="target-drop", current_pp=10)]
        move = make_status_move("target-drop", "target-drop-effect")
        move.power = 1
        battle = make_battle()

        score = evaluate_level_3_weighted(
            battle,
            {"p1": p1, "p2": p2},
            "player",
            movements={"target-drop": move},
            move_effects={"target-drop-effect": make_stat_effect("target-drop-effect", "target", "def", -1)},
            weights={"effects": 1.0},
        )

        assert score > 0.0
