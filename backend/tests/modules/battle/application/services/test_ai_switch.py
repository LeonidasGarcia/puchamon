"""Tests for AI switch behavior during battle."""

import pytest
from puchamon.modules.agentia.application.services.ia_service import IAService
from puchamon.modules.agentia.domain.switch_selectors import RandomSwitchSelector
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance, StatStages


def make_battle_instance(instance_id, trainer_id, current_hp, max_hp, fainted=False, slot=0):
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=slot,
        pokemon_id="Pikachu",
        moveset_id="m1",
        types=["Electric"],
        current_hp=current_hp,
        max_hp=max_hp,
        ability="Static",
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=fainted,
        is_revealed=True,
        revealed_moves=[],
    )


class TestRandomSwitchSelector:
    """Tests for RandomSwitchSelector."""

    def test_selector_finds_available_replacements(self):
        """RandomSwitchSelector should find non-fainted pokemon not currently active."""
        trainer_id = "trainer_ai"

        p1 = make_battle_instance("p1", trainer_id, current_hp=0, max_hp=100, fainted=True)
        p2 = make_battle_instance("p2", trainer_id, current_hp=50, max_hp=100, fainted=False, slot=None)
        p3 = make_battle_instance("p3", trainer_id, current_hp=100, max_hp=100, fainted=False, slot=None)
        p4 = make_battle_instance("p4", trainer_id, current_hp=0, max_hp=100, fainted=True, slot=None)

        from puchamon.modules.battle.domain.entities.battle import Battle, SideState

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_replacements",
            sides={
                trainer_id: SideState(active_pokemon_instance_ids=[None]),
                "opponent": SideState(active_pokemon_instance_ids=["p5"]),
            },
            players=[],
            current_turn_actions=[],
        )

        instances = {"p1": p1, "p2": p2, "p3": p3, "p4": p4}

        selector = RandomSwitchSelector()
        result = selector.select(battle, instances, trainer_id)

        assert result in ["p2", "p3"], f"Should select p2 or p3, got {result}"
        assert result != "p4", "Should not select fainted pokemon"
        assert result != "p1", "Should not select fainted pokemon"

    def test_selector_returns_none_when_no_replacements(self):
        """Selector should return None when no replacement pokemon are available."""
        trainer_id = "trainer_ai"

        p1 = make_battle_instance("p1", trainer_id, current_hp=0, max_hp=100, fainted=True)

        from puchamon.modules.battle.domain.entities.battle import Battle, SideState

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_replacements",
            sides={
                trainer_id: SideState(active_pokemon_instance_ids=[None]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[],
            current_turn_actions=[],
        )

        instances = {"p1": p1}

        selector = RandomSwitchSelector()
        result = selector.select(battle, instances, trainer_id)

        assert result is None, "Should return None when no replacements are available"

    def test_selector_excludes_active_pokemon(self):
        """Selector should not select a pokemon that is currently active."""
        trainer_id = "trainer_ai"

        p1 = make_battle_instance("p1", trainer_id, current_hp=50, max_hp=100, fainted=False, slot=0)
        p2 = make_battle_instance("p2", trainer_id, current_hp=100, max_hp=100, fainted=False, slot=None)

        from puchamon.modules.battle.domain.entities.battle import Battle, SideState

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_actions",
            sides={
                trainer_id: SideState(active_pokemon_instance_ids=["p1"]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[],
            current_turn_actions=[],
        )

        instances = {"p1": p1, "p2": p2}

        selector = RandomSwitchSelector()
        result = selector.select(battle, instances, trainer_id)

        assert result == "p2", "Should select p2 which is not active"
        assert result != "p1", "Should not select p1 which is active"


class TestIAServiceSwitchAction:
    """Tests for IAService.generate_switch_action."""

    @pytest.mark.asyncio
    async def test_ai_generates_switch_action_when_pokemon_faints(self):
        """AI should generate a switch action when its active pokemon faints."""
        from puchamon.modules.agentia.application.services.ia_service import IAService
        from puchamon.modules.battle.domain.entities.battle import Battle, Player, SideState

        ia_service = IAService()
        trainer_id = "trainer_ai"

        fainted_pokemon = make_battle_instance(
            instance_id="p1",
            trainer_id=trainer_id,
            current_hp=0,
            max_hp=100,
            fainted=True,
        )
        alive_replacement = make_battle_instance(
            instance_id="p2",
            trainer_id=trainer_id,
            current_hp=80,
            max_hp=100,
            fainted=False,
            slot=None,
        )

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_replacements",
            sides={
                trainer_id: SideState(active_pokemon_instance_ids=[None]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[Player(trainer_id=trainer_id, name=f"Trainer {trainer_id}", controller_type="ai", ai_level=1)],
            current_turn_actions=[],
        )

        instances = {"p1": fainted_pokemon, "p2": alive_replacement}
        player = battle.players[0]

        action = await ia_service.generate_switch_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=1,
        )

        assert action is not None, "AI should generate a switch action when pokemon faints"
        assert action.type == "switch", "Action type should be switch"
        assert action.replacement_instance_id == "p2", "Should select the alive replacement"

    @pytest.mark.asyncio
    async def test_ai_returns_none_when_no_replacements_available(self):
        """AI should return None when no replacement pokemon are available."""
        from puchamon.modules.agentia.application.services.ia_service import IAService
        from puchamon.modules.battle.domain.entities.battle import Battle, Player, SideState

        ia_service = IAService()
        trainer_id = "trainer_ai"

        fainted_pokemon = make_battle_instance(
            instance_id="p1",
            trainer_id=trainer_id,
            current_hp=0,
            max_hp=100,
            fainted=True,
        )

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_replacements",
            sides={
                trainer_id: SideState(active_pokemon_instance_ids=[None]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[Player(trainer_id=trainer_id, name=f"Trainer {trainer_id}", controller_type="ai", ai_level=1)],
            current_turn_actions=[],
        )

        instances = {"p1": fainted_pokemon}
        player = battle.players[0]

        action = await ia_service.generate_switch_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=1,
        )

        assert action is None, "AI should return None when no replacements are available"

    @pytest.mark.asyncio
    async def test_ai_switch_action_with_empty_active_slot(self):
        """Switch action should work when active slot is None (pokemon already removed)."""
        from puchamon.modules.agentia.application.services.ia_service import IAService
        from puchamon.modules.battle.domain.entities.battle import Battle, Player, SideState

        ia_service = IAService()
        trainer_id = "trainer_ai"

        replacement = make_battle_instance(
            instance_id="p2",
            trainer_id=trainer_id,
            current_hp=100,
            max_hp=100,
            fainted=False,
            slot=None,
        )

        battle = Battle.model_construct(
            id="b1",
            battle_type="1v1",
            turn=1,
            status="active",
            phase="awaiting_replacements",
            sides={
                trainer_id: SideState(active_pokemon_instance_ids=[None]),
                "opponent": SideState(active_pokemon_instance_ids=["p3"]),
            },
            players=[Player(trainer_id=trainer_id, name=f"Trainer {trainer_id}", controller_type="ai", ai_level=1)],
            current_turn_actions=[],
        )

        instances = {"p2": replacement}
        player = battle.players[0]

        action = await ia_service.generate_switch_action(
            player=player,
            battle=battle,
            instances=instances,
            ai_level=1,
        )

        assert action is not None
        assert action.type == "switch"
        assert action.replacement_instance_id == "p2"
        assert action.user_instance_id == ""  # Empty because active slot was None
