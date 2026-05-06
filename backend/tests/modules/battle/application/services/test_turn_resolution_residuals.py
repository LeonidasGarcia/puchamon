import pytest
from unittest.mock import MagicMock
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
from puchamon.modules.pokedex.domain.entities.conditions import Condition, EndTurnDamageEffect, RatioPayload, EndTurnDrainEffect
from puchamon.modules.pokedex.domain.entities.weathers import Weather, EndTurnDamageEffect as WeatherEndTurnDamageEffect, EndTurnDamagePayload

@pytest.fixture
def service():
    return TurnResolutionService(
        action_registry=build_default_action_strategy_registry(),
        move_effect_registry=build_default_move_effect_strategy_registry(),
        condition_effect_registry=build_default_condition_effect_strategy_registry(),
        weather_effect_registry=build_default_weather_effect_strategy_registry(),
    )

def test_resolve_residuals_weather_damage(service):
    # Setup
    instance = BattleInstance.model_construct(
        id="p1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="Pikachu",
        moveset_id="m1",
        types=["Electric"],
        current_hp=100,
        max_hp=100,
        ability="Static",
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=False,
        is_revealed=True,
        revealed_moves=[]
    )
    
    battle = Battle.model_construct(
        id="b1",
        battle_type="1v1",
        turn=1,
        status="active",
        weather=WeatherState(weather_id="sandstorm", remaining_turns=5),
        sides={
            "t1": SideState(hazards=[], active_pokemon_instance_ids=["p1"]),
            "t2": SideState(hazards=[], active_pokemon_instance_ids=[None])
        },
        players=[],
        current_turn_actions=[]
    )
    
    context = BattleStrategyContext(battle=battle, battle_instances={"p1": instance})
    
    sandstorm = Weather.model_construct(
        id="sandstorm",
        name="Sandstorm",
        effects=[
            WeatherEndTurnDamageEffect(
                kind="end_turn_damage",
                payload=EndTurnDamagePayload(ratio=0.0625, immune_types=["Rock", "Ground", "Steel"])
            )
        ]
    )
    
    # Execute
    service._resolve_residuals(context, {}, {"sandstorm": sandstorm})
    
    # Verify
    assert instance.current_hp == 100 - 6 # floor(100 * 0.0625) = 6
    assert any(e.kind == "weather_damage" for e in context.events)

def test_resolve_residuals_poison_damage(service):
    # Setup
    instance = BattleInstance.model_construct(
        id="p1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="Pikachu",
        moveset_id="m1",
        types=["Electric"],
        current_hp=100,
        max_hp=100,
        ability="Static",
        status="poison",
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=False,
        is_revealed=True,
        revealed_moves=[]
    )
    
    battle = Battle.model_construct(
        id="b1",
        battle_type="1v1",
        turn=1,
        status="active",
        sides={
            "t1": SideState(hazards=[], active_pokemon_instance_ids=["p1"]),
            "t2": SideState(hazards=[], active_pokemon_instance_ids=[None])
        },
        players=[],
        current_turn_actions=[]
    )
    
    context = BattleStrategyContext(battle=battle, battle_instances={"p1": instance})
    
    poison = Condition.model_construct(
        id="poison",
        name="Poison",
        category="major",
        effects=[
            EndTurnDamageEffect(kind="end_turn_damage", payload=RatioPayload(ratio=0.125))
        ]
    )
    
    # Execute
    service._resolve_residuals(context, {"poison": poison}, {})
    
    # Verify
    assert instance.current_hp == 100 - 12 # floor(100 * 0.125) = 12
    assert any(e.kind == "condition_damage" for e in context.events)

def test_resolve_residuals_leech_seed(service):
    # Setup
    p1 = BattleInstance.model_construct(
        id="p1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="Pikachu",
        moveset_id="m1",
        types=["Electric"],
        current_hp=100,
        max_hp=100,
        ability="Static",
        volatile_status=["seeded"],
        stages=StatStages(),
        move_state=[],
        fainted=False,
        is_revealed=True,
        revealed_moves=[]
    )
    
    p2 = BattleInstance.model_construct(
        id="p2",
        battle_id="b1",
        trainer_id="t2",
        slot=0,
        pokemon_id="Bulbasaur",
        moveset_id="m2",
        types=["Grass"],
        current_hp=50,
        max_hp=100,
        ability="Overgrow",
        volatile_status=[],
        stages=StatStages(),
        move_state=[],
        fainted=False,
        is_revealed=True,
        revealed_moves=[]
    )
    
    battle = Battle.model_construct(
        id="b1",
        battle_type="1v1",
        turn=1,
        status="active",
        sides={
            "t1": SideState(hazards=[], active_pokemon_instance_ids=["p1"]),
            "t2": SideState(hazards=[], active_pokemon_instance_ids=["p2"])
        },
        players=[],
        current_turn_actions=[]
    )
    
    context = BattleStrategyContext(battle=battle, battle_instances={"p1": p1, "p2": p2})
    
    seeded = Condition.model_construct(
        id="seeded",
        name="Leech Seed",
        category="volatile",
        effects=[
            EndTurnDrainEffect(kind="end_turn_drain", payload=RatioPayload(ratio=0.125))
        ]
    )
    
    # Execute
    service._resolve_residuals(context, {"seeded": seeded}, {})
    
    # Verify
    assert p1.current_hp == 100 - 12
    assert p2.current_hp == 50 + 12
    assert any(e.kind == "condition_drain" for e in context.events)
    assert any(e.kind == "condition_heal" for e in context.events)
