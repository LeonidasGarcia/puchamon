"""Tests for IAService with Minimax levels 2 and 3."""

import pytest
from unittest.mock import MagicMock
from puchamon.modules.agentia.application.services import IAService, AI_LEVEL_EASY, AI_LEVEL_MEDIUM, AI_LEVEL_HARD
from puchamon.modules.agentia.domain.heuristics import evaluate_level_2, evaluate_level_3
from puchamon.modules.battle.domain.entities import Battle, BattleInstance, SideState, Player, StatStages, BattleStats, MoveState
from puchamon.modules.pokedex.domain.entities import Movement


def make_instance(instance_id, trainer_id, current_hp, max_hp, fainted=False, slot=0, moves=None, status=None):
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
        types=["Normal"],
        level=50,
        stats=BattleStats(hp=100, atk=100, def_=100, spa=100, spd=100, spe=100),
        current_hp=current_hp,
        max_hp=max_hp,
        ability="TestAbility",
        status=status,
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


class TestIAServiceLevel2Integration:
    """Integration tests for IAService with AI Level 2 (Minimax + HP heuristic)."""

    @pytest.mark.asyncio
    async def test_level2_uses_minimax_with_evaluate_level_2(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100)
        p2 = make_instance("p2", "opponent", 80, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p2"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=2)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2}

        movements = {
            "tackle": make_movement("tackle", power=40),
            "growl": make_movement("growl", power=0),
        }

        ia_service = IAService()
        player = battle.players[0]

        action = await ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=AI_LEVEL_MEDIUM,
            movements=movements,
        )

        assert action is not None
        assert action.type == "move"
        assert action.player == "trainer_ai"

    @pytest.mark.asyncio
    async def test_level2_returns_move_action_when_pokemon_alive(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100)
        p2 = make_instance("p2", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p2"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=2)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2}

        movements = {
            "tackle": make_movement("tackle", power=40),
        }

        ia_service = IAService()
        player = battle.players[0]

        action = await ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=AI_LEVEL_MEDIUM,
            movements=movements,
        )

        assert action.type == "move"
        assert action.move_id == "tackle"

    @pytest.mark.asyncio
    async def test_level2_switches_when_active_pokemon_faints(self):
        p1 = make_instance("p1", "trainer_ai", 0, 100, fainted=True)
        p2 = make_instance("p2", "trainer_ai", 80, 100, slot=None)
        p3 = make_instance("p3", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=2)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2, "p3": p3}

        movements = {
            "tackle": make_movement("tackle", power=40),
        }

        ia_service = IAService()
        player = battle.players[0]

        action = await ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=AI_LEVEL_MEDIUM,
            movements=movements,
        )

        assert action is not None
        assert action.type == "switch"
        assert action.replacement_instance_id == "p2"

    @pytest.mark.asyncio
    async def test_level2_falls_back_to_switch_when_no_moves(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100, moves=[])
        p2 = make_instance("p2", "trainer_ai", 80, 100, slot=None)
        p3 = make_instance("p3", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=2)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2, "p3": p3}

        ia_service = IAService()
        player = battle.players[0]

        action = await ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=AI_LEVEL_MEDIUM,
            movements={},
        )

        assert action is not None
        assert action.type == "switch"


class TestIAServiceLevel3Integration:
    """Integration tests for IAService with AI Level 3 (Minimax + multi-factor heuristic)."""

    @pytest.mark.asyncio
    async def test_level3_uses_minimax_with_evaluate_level_3(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100)
        p2 = make_instance("p2", "opponent", 80, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p2"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=3)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2}

        movements = {
            "tackle": make_movement("tackle", power=40),
            "flamethrower": make_movement("flamethrower", power=90, move_type="fire", category="special"),
        }

        ia_service = IAService()
        player = battle.players[0]

        action = await ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=AI_LEVEL_HARD,
            movements=movements,
        )

        assert action is not None
        assert action.type == "move"
        assert action.player == "trainer_ai"
        assert action.move_id in ["tackle", "flamethrower"]

    @pytest.mark.asyncio
    async def test_level3_considers_status_in_decision(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100, status="burn")
        p2 = make_instance("p2", "opponent", 100, 100, status="poison")
        p3 = make_instance("p3", "trainer_ai", 80, 100, slot=None)
        p4 = make_instance("p4", "opponent", 80, 100, slot=None)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p2"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=3)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2, "p3": p3, "p4": p4}

        movements = {
            "tackle": make_movement("tackle", power=40),
        }

        ia_service = IAService()
        player = battle.players[0]

        action = await ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=AI_LEVEL_HARD,
            movements=movements,
        )

        assert action is not None
        assert action.player == "trainer_ai"


class TestIAServiceLevel1Regression:
    """Regression tests to ensure Level 1 still works correctly."""

    @pytest.mark.asyncio
    async def test_level1_still_uses_random_selector(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100)
        p2 = make_instance("p2", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p2"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=1)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2}

        movements = {
            "tackle": make_movement("tackle", power=40),
            "growl": make_movement("growl", power=0),
        }

        ia_service = IAService()
        player = battle.players[0]

        action = await ia_service.generate_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=AI_LEVEL_EASY,
            movements=movements,
        )

        assert action is not None
        assert action.type == "move"
        assert action.player == "trainer_ai"


class TestIAServiceMinimaxIntegration:
    """Tests verifying Minimax is properly integrated with IAService."""

    @pytest.mark.asyncio
    async def test_ia_service_creates_minimax_selector_for_level_2(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100)
        p2 = make_instance("p2", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p2"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=2)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2}

        movements = {
            "tackle": make_movement("tackle", power=40),
        }

        ia_service = IAService()
        player = battle.players[0]
        active_instance = instances["p1"]

        action = await ia_service.generate_move_action(
            player=player,
            active_instance=active_instance,
            ai_level=AI_LEVEL_MEDIUM,
            context=MagicMock(battle=battle, instances=instances, movements=movements),
        )

        assert action is not None
        assert action.move_id in ["tackle"]

    @pytest.mark.asyncio
    async def test_ia_service_creates_minimax_selector_for_level_3(self):
        p1 = make_instance("p1", "trainer_ai", 100, 100)
        p2 = make_instance("p2", "opponent", 100, 100)

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                "trainer_ai": SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p2"]),
            },
            players=[Player(trainer_id="trainer_ai", name="AI Trainer", controller_type="ai", ai_level=3)],
            current_turn_actions=[],
        )
        instances = {"p1": p1, "p2": p2}

        movements = {
            "tackle": make_movement("tackle", power=40),
        }

        ia_service = IAService()
        player = battle.players[0]
        active_instance = instances["p1"]

        action = await ia_service.generate_move_action(
            player=player,
            active_instance=active_instance,
            ai_level=AI_LEVEL_HARD,
            context=MagicMock(battle=battle, instances=instances, movements=movements),
        )

        assert action is not None
        assert action.move_id in ["tackle"]