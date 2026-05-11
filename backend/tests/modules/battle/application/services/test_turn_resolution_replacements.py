import pytest
from puchamon.modules.battle.application.services.turn_resolution_service import TurnResolutionService
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, WeatherState
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance, StatStages
from puchamon.modules.battle.domain.registries import (
    build_default_action_strategy_registry,
    build_default_condition_effect_strategy_registry,
    build_default_move_effect_strategy_registry,
    build_default_weather_effect_strategy_registry,
)
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext


@pytest.fixture
def service():
    return TurnResolutionService(
        action_registry=build_default_action_strategy_registry(),
        move_effect_registry=build_default_move_effect_strategy_registry(),
        condition_effect_registry=build_default_condition_effect_strategy_registry(),
        weather_effect_registry=build_default_weather_effect_strategy_registry(),
    )


def test_fainted_pokemon_leaves_slot_empty_for_manual_replacement(service):
    """
    Test that when a pokemon faints mid-turn, the slot becomes empty and is NOT
    automatically filled. The phase should become 'awaiting_replacements' at the end.
    """
    # Active pokemon that will faint
    p1 = BattleInstance.model_construct(
        id="p1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="Pikachu",
        moveset_id="m1",
        types=["Electric"],
        current_hp=0,
        max_hp=100,
        ability="Static",
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=True,
        is_revealed=True,
        revealed_moves=[],
    )
    # Available replacement in the party
    p2 = BattleInstance.model_construct(
        id="p2",
        battle_id="b1",
        trainer_id="t1",
        slot=None,
        pokemon_id="Bulbasaur",
        moveset_id="m2",
        types=["Grass"],
        current_hp=100,
        max_hp=100,
        ability="Overgrow",
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=False,
        is_revealed=False,
        revealed_moves=[],
    )

    # Opponent
    p3 = BattleInstance.model_construct(
        id="p3",
        battle_id="b1",
        trainer_id="t2",
        slot=0,
        pokemon_id="Charmander",
        moveset_id="m3",
        types=["Fire"],
        current_hp=100,
        max_hp=100,
        ability="Blaze",
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=False,
        is_revealed=True,
        revealed_moves=[],
    )

    battle = Battle.model_construct(
        id="b1",
        battle_type="1v1",
        turn=1,
        status="active",
        phase="awaiting_actions",
        sides={
            "t1": SideState(hazards=[], active_pokemon_instance_ids=[None]),  # Slot is None because p1 fainted
            "t2": SideState(hazards=[], active_pokemon_instance_ids=["p3"]),
        },
        players=[],
        current_turn_actions=[],
    )

    context = service.resolve_turn(
        battle=battle,
        instances={"p1": p1, "p2": p2, "p3": p3},
        actions=[],
        movements={},
        conditions={},
        weathers={},
        move_effects={},
        type_chart={},
    )

    # It should NOT auto-replace
    assert context.battle.sides["t1"].active_pokemon_instance_ids[0] is None, "Expected slot to remain empty for manual replacement"

    assert context.battle.phase == "awaiting_replacements", "Expected phase to transition to awaiting_replacements"
