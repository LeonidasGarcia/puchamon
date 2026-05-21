import pytest
from unittest.mock import patch

from puchamon.modules.battle.domain.strategies.actions.switch_action_strategy import SwitchActionStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ActionExecutionInput
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, Player, TurnAction, TargetScope
from puchamon.modules.battle.domain.exceptions import BattleValidationError, BattleConflictError


def _build_base_instance(instance_id: str, trainer_id: str, pokemon_id: str, fainted: bool = False) -> BattleInstance:
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=0,
        pokemon_id=pokemon_id,
        moveset_id="m1",
        types=["normal"],
        current_hp=0 if fainted else 100,
        max_hp=100,
        status=None,
        fainted=fainted,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return SwitchActionStrategy()


def test_invalid_action_type(strategy):
    action = TurnAction.model_construct(
        type="move",
        player="t1",
        user_instance_id="inst_1",
        move_id="tackle",
        target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0),
    )
    execution = ActionExecutionInput(action=action)
    with pytest.raises(BattleValidationError, match="cannot execute action type"):
        strategy.execute(
            BattleStrategyContext(
                battle=Battle.model_construct(
                    id="b1", format="singles", side_1=SideState.model_construct(), side_2=SideState.model_construct(), turn=1
                ),
                battle_instances={},
            ),
            execution,
        )


def test_missing_replacement_id(strategy):
    action = TurnAction.model_construct(
        type="switch", player="t1", user_instance_id="inst_1", target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0)
    )
    execution = ActionExecutionInput(action=action, replacement_instance_id=None)
    with pytest.raises(BattleValidationError, match="require a replacement instance id"):
        strategy.execute(
            BattleStrategyContext(
                battle=Battle.model_construct(
                    id="b1", format="singles", side_1=SideState.model_construct(), side_2=SideState.model_construct(), turn=1
                ),
                battle_instances={},
            ),
            execution,
        )


def test_switch_empty_slot(strategy):
    replacement = _build_base_instance("inst_2", "t1", "charmander")
    action = TurnAction.model_construct(
        type="switch", player="t1", user_instance_id="", target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0)
    )
    execution = ActionExecutionInput(action=action, replacement_instance_id="inst_2")

    battle = Battle.model_construct(
        id="b1",
        format="1v1",
        status="active",
        turn=1,
        sides={
            "t1": SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_2"])], active_pokemon_instance_ids=[None])
        },
        players=[Player.model_construct(id="t1", instance_ids=["inst_2"])],
        current_turn_actions=[],
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_2": replacement})

    strategy.execute(context, execution)

    assert battle.sides["t1"].active_pokemon_instance_ids[0] == "inst_2"
    assert replacement.is_revealed is True
    assert context.events[0].kind == "replacement"


def test_switch_different_trainer(strategy):
    source = _build_base_instance("inst_1", "t1", "pikachu")
    replacement = _build_base_instance("inst_2", "t2", "charmander")
    action = TurnAction.model_construct(
        type="switch", player="t1", user_instance_id="inst_1", target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0)
    )
    execution = ActionExecutionInput(action=action, replacement_instance_id="inst_2")

    battle = Battle.model_construct(
        id="b1",
        format="singles",
        turn=1,
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": source, "inst_2": replacement})

    with pytest.raises(BattleValidationError, match="belong to the same trainer"):
        strategy.execute(context, execution)


def test_switch_fainted_replacement(strategy):
    source = _build_base_instance("inst_1", "t1", "pikachu")
    replacement = _build_base_instance("inst_2", "t1", "charmander", fainted=True)
    action = TurnAction.model_construct(
        type="switch", player="t1", user_instance_id="inst_1", target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0)
    )
    execution = ActionExecutionInput(action=action, replacement_instance_id="inst_2")

    battle = Battle.model_construct(
        id="b1",
        format="singles",
        turn=1,
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": source, "inst_2": replacement})

    with pytest.raises(BattleConflictError, match="A fainted pokemon cannot enter"):
        strategy.execute(context, execution)


def test_switch_active_pokemon(strategy):
    source = _build_base_instance("inst_1", "t1", "pikachu")
    replacement = _build_base_instance("inst_2", "t1", "charmander")
    action = TurnAction.model_construct(
        type="switch", player="t1", user_instance_id="inst_1", target=TargetScope(scope="target", target_side="foe_side", target_active_slot=0)
    )
    execution = ActionExecutionInput(action=action, replacement_instance_id="inst_2")

    battle = Battle.model_construct(
        id="b1",
        format="1v1",
        status="active",
        turn=1,
        sides={
            "t1": SideState.model_construct(
                players=[Player.model_construct(id="t1", instance_ids=["inst_1", "inst_2"])], active_pokemon_instance_ids=["inst_1"]
            )
        },
        players=[Player.model_construct(id="t1", instance_ids=["inst_1", "inst_2"])],
        current_turn_actions=[],
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": source, "inst_2": replacement})

    strategy.execute(context, execution)

    assert battle.sides["t1"].active_pokemon_instance_ids[0] == "inst_2"
    assert replacement.is_revealed is True
    assert context.events[0].kind == "switch"
    assert "switched out" in context.events[0].message
