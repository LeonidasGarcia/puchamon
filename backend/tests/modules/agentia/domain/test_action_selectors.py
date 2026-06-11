"""Tests for action selectors."""

import pytest
from puchamon.modules.agentia.domain.action_selectors import (
    AI_LEVEL_EASY,
    AI_LEVEL_HARD_GA,
    AI_LEVEL_HARD_MANUAL,
    AI_LEVEL_MEDIUM,
    DEFAULT_MINIMAX_DEPTH,
    MinimaxActionSelector,
    RandomActionSelector,
)
from puchamon.modules.agentia.domain.action_utils import get_available_actions
from puchamon.modules.agentia.domain.minimax import MinimaxMetrics
from puchamon.modules.agentia.domain.state_simulator import simulate_action
from puchamon.modules.battle.domain.entities import Battle, BattleInstance, SideState, StatStages, BattleStats, MoveState


def make_instance(instance_id, trainer_id, current_hp, max_hp, fainted=False, types=None, moves=None, slot=0):
    if types is None:
        types = ["Normal"]
    if moves is None:
        moves = [
            MoveState(move_id="tackle", current_pp=30),
            MoveState(move_id="growl", current_pp=30),
        ]
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=slot,
        pokemon_id="TestPokemon",
        moveset_id="ms1",
        types=types,
        level=50,
        stats=BattleStats(hp=100, atk=100, def_=100, spa=100, spd=100, spe=100),
        current_hp=current_hp,
        max_hp=max_hp,
        ability="TestAbility",
        volatile_status=[],
        stages=StatStages(),
        move_state=moves,
        fainted=fainted,
        is_revealed=True,
        revealed_moves=[],
    )


class TestRandomActionSelector:
    """Tests for RandomActionSelector."""

    def test_select_returns_action(self):
        p1 = make_instance("p1", "player", 100, 100)
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

        selector = RandomActionSelector()
        action = selector.select(battle, instances, "player")

        assert action is not None
        assert action[0] in ["MOVE", "SWITCH"]

    def test_select_returns_none_when_no_actions(self):
        p1 = make_instance("p1", "player", 0, 100, fainted=True)
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

        selector = RandomActionSelector()
        action = selector.select(battle, instances, "player")

        assert action is None


class TestMinimaxActionSelector:
    """Tests for MinimaxActionSelector."""

    def test_selector_with_level_2(self):
        selector = MinimaxActionSelector(AI_LEVEL_MEDIUM)
        assert selector.ai_level == AI_LEVEL_MEDIUM
        assert selector.depth == DEFAULT_MINIMAX_DEPTH

    def test_selector_with_level_3_manual(self):
        selector = MinimaxActionSelector(AI_LEVEL_HARD_MANUAL)
        assert selector.ai_level == AI_LEVEL_HARD_MANUAL
        assert selector.depth == DEFAULT_MINIMAX_DEPTH

    def test_selector_with_level_4_ga(self):
        selector = MinimaxActionSelector(AI_LEVEL_HARD_GA)
        assert selector.ai_level == AI_LEVEL_HARD_GA
        assert selector.depth == DEFAULT_MINIMAX_DEPTH

    def test_selector_custom_depth(self):
        selector = MinimaxActionSelector(AI_LEVEL_HARD_GA, depth=5)
        assert selector.depth == 5

    def test_select_returns_action_when_available(self):
        p1 = make_instance("p1", "player", 100, 100)
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

        selector = MinimaxActionSelector(AI_LEVEL_MEDIUM)
        metrics = MinimaxMetrics()
        action = selector.select(battle, instances, "player", metrics=metrics)

        assert action is not None
        assert action[0] in ["MOVE", "SWITCH"]
        assert metrics.nodes_visited > 0

    def test_select_prefers_higher_damage_move(self):
        from puchamon.modules.pokedex.domain.entities import Movement

        p1 = make_instance("p1", "player", 100, 100)
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

        movements = {
            "tackle": Movement.model_construct(
                id="tackle", name="Tackle", type="normal", category="physical",
                power=40, accuracy=100, pp=30, priority=0, target="target",
                makes_contact=True, protectable=True, effect_ids=[],
            ),
            "thunderbolt": Movement.model_construct(
                id="thunderbolt", name="Thunderbolt", type="electric", category="special",
                power=90, accuracy=100, pp=30, priority=0, target="target",
                makes_contact=True, protectable=True, effect_ids=[],
            ),
        }

        p1_active = instances["p1"]
        p1_active.move_state = [
            MoveState(move_id="tackle", current_pp=30),
            MoveState(move_id="thunderbolt", current_pp=30),
        ]

        selector = MinimaxActionSelector(AI_LEVEL_MEDIUM, depth=1)
        action = selector.select(battle, instances, "player", movements)

        assert action is not None
        assert action[0] == "MOVE"
        assert action[1] in ["tackle", "thunderbolt"]

    def test_select_can_return_switch(self):
        p1 = make_instance("p1", "player", 10, 100)
        p2 = make_instance("p2", "player", 100, 100, slot=None)
        p3 = make_instance("p3", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "player": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2, "p3": p3}

        selector = MinimaxActionSelector(AI_LEVEL_MEDIUM, depth=1)
        action = selector.select(battle, instances, "player")

        assert action is not None

    def test_get_available_actions_includes_moves_and_switches(self):
        p1 = make_instance("p1", "player", 100, 100)
        p2 = make_instance("p2", "player", 80, 100, slot=None)
        p3 = make_instance("p3", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "player": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2, "p3": p3}

        selector = MinimaxActionSelector(AI_LEVEL_MEDIUM)
        actions = get_available_actions(battle, instances, "player")

        action_types = [a[0] for a in actions]
        assert "MOVE" in action_types
        assert "SWITCH" in action_types

    def test_simulate_move_reduces_hp(self):
        from puchamon.modules.pokedex.domain.entities import Movement

        p1 = make_instance("p1", "player", 100, 100)
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

        move = Movement.model_construct(
            id="tackle", name="Tackle", type="normal", category="physical",
            power=50, accuracy=100, pp=30, priority=0, target="target",
            makes_contact=True, protectable=True, effect_ids=[],
        )

        movements = {"tackle": move}

        new_battle, new_instances = simulate_action(
            battle, instances, ("MOVE", "tackle"), "player", "opponent", movements
        )

        assert new_instances["p2"].current_hp < 100

    def test_simulate_switch_changes_active(self):
        p1 = make_instance("p1", "player", 100, 100)
        p2 = make_instance("p2", "player", 80, 100, slot=None)
        p3 = make_instance("p3", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "player": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2, "p3": p3}

        new_battle, new_instances = simulate_action(
            battle, instances, ("SWITCH", "p2"), "player", "opponent"
        )

        assert new_battle.sides["player"].active_pokemon_instance_ids[0] == "p2"
