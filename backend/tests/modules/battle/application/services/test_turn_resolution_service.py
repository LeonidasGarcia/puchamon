import pytest
from unittest.mock import MagicMock
from puchamon.modules.battle.application.services.turn_resolution_service import TurnResolutionService, _ResolveTurnParams
from puchamon.modules.battle.domain.entities import Battle, BattleInstance, SideState, TurnAction, StatStages, BattleStats
from puchamon.modules.battle.domain.runtime import BattleStrategyContext
from puchamon.modules.pokedex.domain.entities import Movement


@pytest.fixture
def action_registry():
    return MagicMock()


@pytest.fixture
def move_effect_registry():
    return MagicMock()


@pytest.fixture
def condition_effect_registry():
    return MagicMock()


@pytest.fixture
def turn_service(action_registry, move_effect_registry, condition_effect_registry):
    return TurnResolutionService(action_registry, move_effect_registry, condition_effect_registry)


def _build_base_instance(instance_id, trainer_id, speed=100) -> BattleInstance:
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=0,
        pokemon_id="pkmn",
        moveset_id="m1",
        types=["normal"],
        current_hp=100,
        max_hp=100,
        stats=BattleStats(hp=100, atk=100, def_=100, spa=100, spd=100, spe=speed),
        stages=StatStages(),
        fainted=False,
        volatile_status=[],
    )


def test_sort_actions_by_priority(turn_service):
    inst1 = _build_base_instance("inst1", "t1", speed=100)
    inst2 = _build_base_instance("inst2", "t2", speed=200) # Faster, but lower priority
    
    battle = Battle.model_construct(id="b1", turn=1)
    context = MagicMock()
    context.get_instance.side_effect = lambda id: inst1 if id == "inst1" else inst2
    
    # Move 1: Priority 1
    move1 = Movement.model_construct(id="quick-attack", name="Quick Attack", priority=1)
    # Move 2: Priority 0
    move2 = Movement.model_construct(id="tackle", name="Tackle", priority=0)
    
    movements = {"quick-attack": move1, "tackle": move2}
    
    actions = [
        TurnAction(player="t2", type="move", user_instance_id="inst2", move_id="tackle"),
        TurnAction(player="t1", type="move", user_instance_id="inst1", move_id="quick-attack"),
    ]
    
    sorted_actions = turn_service._sort_actions(context, actions, movements, {})
    
    assert sorted_actions[0].user_instance_id == "inst1"  # Quick Attack goes first
    assert sorted_actions[1].user_instance_id == "inst2"


def test_sort_actions_by_speed(turn_service):
    inst1 = _build_base_instance("inst1", "t1", speed=100)
    inst2 = _build_base_instance("inst2", "t2", speed=200) # Faster
    
    battle = Battle.model_construct(id="b1", turn=1)
    context = MagicMock()
    context.get_instance.side_effect = lambda id: inst1 if id == "inst1" else inst2
    
    move = Movement.model_construct(id="tackle", name="Tackle", priority=0)
    movements = {"tackle": move}
    
    actions = [
        TurnAction(player="t1", type="move", user_instance_id="inst1", move_id="tackle"),
        TurnAction(player="t2", type="move", user_instance_id="inst2", move_id="tackle"),
    ]
    
    sorted_actions = turn_service._sort_actions(context, actions, movements, {})
    
    assert sorted_actions[0].user_instance_id == "inst2"  # Faster goes first
    assert sorted_actions[1].user_instance_id == "inst1"


def test_resolve_switches_first(turn_service, action_registry):
    battle = Battle.model_construct(id="b1", turn=1)
    context = MagicMock()
    
    switch_action = TurnAction(player="t1", type="switch", user_instance_id="inst1", replacement_instance_id="inst3")
    move_action = TurnAction(player="t2", type="move", user_instance_id="inst2", move_id="tackle")
    
    # Mock Switch Strategy
    switch_strategy = MagicMock()
    action_registry.get.return_value = switch_strategy
    
    turn_service._resolve_switches(context, [switch_action, move_action])
    
    # Switch should be called
    assert switch_strategy.execute.called
    args, _ = switch_strategy.execute.call_args
    assert args[1].action.type == "switch"


def test_resolve_turn_full_flow(turn_service, action_registry):
    # This test verifies that all major steps of resolve_turn are called
    battle = Battle.model_construct(
        id="b1", 
        turn=1, 
        sides={"t1": SideState(active_pokemon_instance_ids=["inst1"]), "t2": SideState(active_pokemon_instance_ids=["inst2"])}
    )
    inst1 = _build_base_instance("inst1", "t1")
    inst2 = _build_base_instance("inst2", "t2")
    
    params = _ResolveTurnParams(
        battle=battle,
        instances={"inst1": inst1, "inst2": inst2},
        actions=[],
        movements={},
        conditions={},
        move_effects={},
        type_chart={},
    )
    
    # We can mock the internal methods to see if they are called
    turn_service._resolve_switches = MagicMock()
    turn_service._sort_actions = MagicMock(return_value=[])
    turn_service._execute_actions = MagicMock()
    turn_service._resolve_residuals = MagicMock()
    turn_service._resolve_faints_and_cleanup = MagicMock()
    
    context = turn_service.resolve_turn(params)
    
    assert turn_service._resolve_switches.called
    assert turn_service._sort_actions.called
    assert turn_service._execute_actions.called
    assert turn_service._resolve_residuals.called
    assert turn_service._resolve_faints_and_cleanup.called
    assert isinstance(context, BattleStrategyContext)
