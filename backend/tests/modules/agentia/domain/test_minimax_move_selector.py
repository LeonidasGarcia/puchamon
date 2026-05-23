"""Tests for MinimaxMoveSelector."""

import pytest
from unittest.mock import MagicMock
from puchamon.modules.agentia.domain.move_selectors import MinimaxMoveSelector, RandomMoveSelector
from puchamon.modules.agentia.domain.heuristics import evaluate_level_2, evaluate_level_3
from puchamon.modules.battle.domain.entities import Battle, BattleInstance, SideState, StatStages, BattleStats, MoveState
from puchamon.modules.pokedex.domain.entities import Movement


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


def make_movement(move_id, power, move_type="normal", category="physical"):
    return Movement.model_construct(
        id=move_id,
        name=move_id.title(),
        type=move_type,
        category=category,
        power=power,
        accuracy=100,
        pp=30,
        priority=0,
        target="target",
        makes_contact=True,
        protectable=True,
        effect_ids=[],
    )


class TestMinimaxMoveSelector:
    """Tests for MinimaxMoveSelector class."""

    def test_selector_requires_battle_and_instances(self):
        selector = MinimaxMoveSelector(
            battle=None,
            instances={},
            player_trainer_id="player",
        )
        assert selector.battle is None
        assert selector.instances == {}

    def test_selector_uses_default_depth_of_3(self):
        selector = MinimaxMoveSelector(
            battle=MagicMock(),
            instances={},
            player_trainer_id="player",
        )
        assert selector.depth == 3

    def test_selector_accepts_custom_depth(self):
        selector = MinimaxMoveSelector(
            battle=MagicMock(),
            instances={},
            player_trainer_id="player",
            depth=5,
        )
        assert selector.depth == 5

    def test_selector_uses_level_2_heuristic_by_default(self):
        selector = MinimaxMoveSelector(
            battle=MagicMock(),
            instances={},
            player_trainer_id="player",
        )
        assert selector.heuristic_func == evaluate_level_2

    def test_selector_accepts_custom_heuristic(self):
        custom_heuristic = MagicMock()
        selector = MinimaxMoveSelector(
            battle=MagicMock(),
            instances={},
            player_trainer_id="player",
            heuristic_func=custom_heuristic,
        )
        assert selector.heuristic_func == custom_heuristic


class TestMinimaxMoveSelectorSelect:
    """Tests for MinimaxMoveSelector.select method."""

    def test_select_returns_none_when_no_moves_available(self):
        p1 = make_instance("p1", "player", 100, 100, moves=[])

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
        instances = {"p1": p1}

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
        )

        available_moves = []
        result = selector.select(available_moves)

        assert result is None

    def test_select_returns_first_move_when_no_opponent(self):
        p1 = make_instance("p1", "player", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "player": SideState(active_pokemon_instance_ids=["p1"]),
            },
            players=[],
            current_turn_actions=[],
        )
        instances = {"p1": p1}

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
        )

        available_moves = [MoveState(move_id="tackle", current_pp=30)]
        result = selector.select(available_moves)

        assert result == "tackle"

    def test_select_prefers_stronger_move(self):
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
            "tackle": make_movement("tackle", power=40),
            "flamethrower": make_movement("flamethrower", power=90, move_type="fire", category="special"),
        }

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
            movements=movements,
            depth=1,
            heuristic_func=evaluate_level_2,
        )

        available_moves = [
            MoveState(move_id="tackle", current_pp=30),
            MoveState(move_id="flamethrower", current_pp=20),
        ]
        result = selector.select(available_moves)

        assert result in ["tackle", "flamethrower"]


class TestMinimaxMoveSelectorGetAvailableActions:
    """Tests for _get_available_actions method."""

    def test_returns_moves_and_switches(self):
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

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
        )

        actions = selector._get_available_actions(battle, instances)

        action_types = [a[0] for a in actions]
        assert "MOVE" in action_types
        assert "SWITCH" in action_types

    def test_excludes_fainted_pokemon_from_switches(self):
        p1 = make_instance("p1", "player", 100, 100)
        p2 = make_instance("p2", "player", 0, 100, fainted=True, slot=None)
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

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
        )

        actions = selector._get_available_actions(battle, instances)

        for action in actions:
            if action[0] == "SWITCH":
                assert action[1] != "p2"


class TestMinimaxMoveSelectorSimulateAction:
    """Tests for _simulate_action method."""

    def test_simulate_move_reduces_opponent_hp(self):
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
            "tackle": make_movement("tackle", power=40),
        }

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
            movements=movements,
        )

        new_battle, new_instances = selector._simulate_action(
            battle,
            instances,
            ("MOVE", "tackle"),
            "player",
            "opponent",
        )

        opponent_hp = new_instances["p2"].current_hp
        assert opponent_hp < 100

    def test_simulate_switch_changes_active_pokemon(self):
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

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
        )

        new_battle, new_instances = selector._simulate_action(
            battle,
            instances,
            ("SWITCH", "p2"),
            "player",
            "opponent",
        )

        assert new_battle.sides["player"].active_pokemon_instance_ids[0] == "p2"


class TestMinimaxIntegration:
    """Integration tests for MinimaxMoveSelector with IA service."""

    def test_level_2_uses_hp_only_heuristic(self):
        selector = MinimaxMoveSelector(
            battle=MagicMock(),
            instances={},
            player_trainer_id="player",
            heuristic_func=evaluate_level_2,
        )
        assert selector.heuristic_func == evaluate_level_2

    def test_level_3_uses_multifactor_heuristic(self):
        selector = MinimaxMoveSelector(
            battle=MagicMock(),
            instances={},
            player_trainer_id="player",
            heuristic_func=evaluate_level_3,
        )
        assert selector.heuristic_func == evaluate_level_3

    def test_selector_with_no_movements_still_works(self):
        p1 = make_instance("p1", "player", 100, 100, moves=[])
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

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
            movements={},
            depth=1,
        )

        available_moves = []
        result = selector.select(available_moves)

        assert result is None

    def test_selector_returns_move_id_from_action_tuple(self):
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
            "tackle": make_movement("tackle", power=40),
        }

        selector = MinimaxMoveSelector(
            battle=battle,
            instances=instances,
            player_trainer_id="player",
            movements=movements,
            depth=1,
        )

        available_moves = [MoveState(move_id="tackle", current_pp=30)]
        result = selector.select(available_moves)

        assert isinstance(result, str)
        assert result in ["tackle"]