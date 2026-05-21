import pytest
from unittest.mock import patch

from puchamon.modules.battle.domain.strategies.conditions.skip_action_condition_effect_strategy import SkipActionConditionEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import SkipActionEffect, EmptyPayload, Condition
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, Player


def _build_base_instance() -> BattleInstance:
    return BattleInstance.model_construct(
        id="inst_1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="pikachu",
        moveset_id="m1",
        types=["electric"],
        current_hp=100,
        max_hp=100,
        status="sleep",
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return SkipActionConditionEffectStrategy()


def test_skip_action_blocks_move(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="sleep", name="Sleep", category="major", effects=[])
    effect = SkipActionEffect(kind="skip_action", payload=EmptyPayload())

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    strategy.apply(context, execution)

    assert context.get_action_block_reason("inst_1") == "skip_action"
    assert len(context.events) == 1
    assert context.events[0].kind == "action_skipped"


def test_skip_action_fainted_pokemon(strategy):
    instance = _build_base_instance()
    instance.current_hp = 0
    instance.fainted = True

    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="sleep", name="Sleep", category="major", effects=[])
    effect = SkipActionEffect(kind="skip_action", payload=EmptyPayload())

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    strategy.apply(context, execution)

    assert context.get_action_block_reason("inst_1") is None
    assert len(context.events) == 0
