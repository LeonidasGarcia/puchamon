import pytest
from unittest.mock import MagicMock
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, Player, TurnAction, TargetScope
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance, StatStages
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ActionExecutionInput
from puchamon.modules.battle.domain.strategies.actions.move_action_strategy import MoveActionStrategy
from puchamon.modules.pokedex.domain.entities import Movement, MoveEffect, Condition
from puchamon.modules.pokedex.domain.entities.conditions import BlockProtectableMovesEffect, EmptyPayload
from puchamon.modules.pokedex.domain.entities.effects import DamagePayload
from puchamon.modules.battle.domain.registries import (
    build_default_move_effect_strategy_registry,
    build_default_condition_effect_strategy_registry,
)


@pytest.fixture
def move_action_strategy():
    return MoveActionStrategy()


@pytest.fixture
def move_registry():
    return build_default_move_effect_strategy_registry()


@pytest.fixture
def condition_registry():
    return build_default_condition_effect_strategy_registry()


def _build_base_instance(instance_id: str, trainer_id: str, pokemon_id: str) -> BattleInstance:
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=0,
        pokemon_id=pokemon_id,
        moveset_id="m1",
        types=["normal"],
        current_hp=100,
        max_hp=100,
        ability="pressure",
        status=None,
        volatile_status=[],
        stages=StatStages(),
        move_state=[MagicMock(move_id="tackle", current_pp=10)],
        fainted=False,
        is_revealed=True,
        revealed_moves=[],
    )


def test_protect_blocks_protectable_move(move_action_strategy, move_registry, condition_registry):
    attacker = _build_base_instance("p1", "t1", "Pikachu")
    defender = _build_base_instance("p2", "t2", "Bulbasaur")
    defender.volatile_status.append("protect")

    battle = Battle.model_construct(
        id="b1",
        battle_type="1v1",
        turn=1,
        status="active",
        sides={
            "t1": SideState(active_pokemon_instance_ids=["p1"]),
            "t2": SideState(active_pokemon_instance_ids=["p2"]),
        },
        players=[Player(trainer_id="t1", name="P1", controller_type="human"), Player(trainer_id="t2", name="P2", controller_type="human")],
        current_turn_actions=[],
    )

    context = BattleStrategyContext(battle=battle, battle_instances={"p1": attacker, "p2": defender})

    movement = Movement.model_construct(
        id="tackle",
        name="Tackle",
        type="normal",
        category="physical",
        power=40,
        accuracy=100,
        pp=35,
        priority=0,
        target="target",
        makes_contact=True,
        protectable=True,  # THIS IS PROTECTABLE
        effect_ids=["effect-damage"],
    )

    dummy_effect = MoveEffect.model_construct(id="effect-damage", kind="damage", target="target", chance=100, order=1, payload=DamagePayload(hits=1))

    action = TurnAction.model_construct(
        type="move",
        player="t1",
        user_instance_id="p1",
        target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0),
        move_id="tackle",
    )

    protect_condition = Condition.model_construct(
        id="protect",
        name="Protect",
        category="volatile",
        effects=[BlockProtectableMovesEffect(kind="block_protectable_moves", payload=EmptyPayload())],
    )

    execution = ActionExecutionInput(
        action=action,
        movement=movement,
        move_effects=[dummy_effect],
        move_effect_strategy_registry=move_registry,
        condition_effect_strategy_registry=condition_registry,
        conditions={"protect": protect_condition},
    )

    move_action_strategy.execute(context, execution)

    # Assertions
    events = context.events
    assert any(e.kind == "move_blocked" for e in events), "Expected a 'move_blocked' event to be emitted"
    assert events[-1].kind == "move_blocked"
    assert "protected itself" in events[-1].message


def test_protect_allows_unprotectable_move(move_action_strategy, move_registry, condition_registry):
    attacker = _build_base_instance("p1", "t1", "Pikachu")
    defender = _build_base_instance("p2", "t2", "Bulbasaur")
    defender.volatile_status.append("protect")

    battle = Battle.model_construct(
        id="b1",
        battle_type="1v1",
        turn=1,
        status="active",
        sides={
            "t1": SideState(active_pokemon_instance_ids=["p1"]),
            "t2": SideState(active_pokemon_instance_ids=["p2"]),
        },
        players=[Player(trainer_id="t1", name="P1", controller_type="human"), Player(trainer_id="t2", name="P2", controller_type="human")],
        current_turn_actions=[],
    )

    context = BattleStrategyContext(battle=battle, battle_instances={"p1": attacker, "p2": defender})

    movement = Movement.model_construct(
        id="feint",
        name="Feint",
        type="normal",
        category="physical",
        power=30,
        accuracy=100,
        pp=10,
        priority=2,
        target="target",
        makes_contact=True,
        protectable=False,  # NOT PROTECTABLE
        effect_ids=["effect-damage"],
    )

    dummy_effect = MoveEffect.model_construct(id="effect-damage", kind="damage", target="target", chance=100, order=1, payload=DamagePayload(hits=1))

    # Need to mock the move state PP check
    attacker.move_state[0].move_id = "feint"

    action = TurnAction.model_construct(
        type="move",
        player="t1",
        user_instance_id="p1",
        target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0),
        move_id="feint",
    )

    protect_condition = Condition.model_construct(
        id="protect",
        name="Protect",
        category="volatile",
        effects=[BlockProtectableMovesEffect(kind="block_protectable_moves", payload=EmptyPayload())],
    )

    execution = ActionExecutionInput(
        action=action,
        movement=movement,
        move_effects=[dummy_effect],
        move_effect_strategy_registry=move_registry,
        condition_effect_strategy_registry=condition_registry,
        conditions={"protect": protect_condition},
    )

    # Just mock calculate_accuracy to True so it doesn't fail there
    import puchamon.modules.battle.domain.strategies.actions.move_action_strategy as mas

    original_accuracy = mas.calculate_accuracy
    mas.calculate_accuracy = lambda *args: True

    try:
        move_action_strategy.execute(context, execution)
    finally:
        mas.calculate_accuracy = original_accuracy

    # Assertions
    events = context.events
    assert all(
        e.kind != "move_blocked" for e in events
    ), "Expected no 'move_blocked' event for an unprotectable move"
    assert any(e.kind == "move_used" for e in events)
