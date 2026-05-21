import pytest
from unittest.mock import patch

from puchamon.modules.battle.domain.strategies.conditions.full_paralysis_chance_condition_effect_strategy import (
    FullParalysisChanceConditionEffectStrategy,
)
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import FullParalysisChanceEffect, ChancePayload, Condition
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
        status="paralyze",
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return FullParalysisChanceConditionEffectStrategy()


def test_paralysis_blocks_move(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="paralyze", name="Paralyze", category="major", effects=[])
    effect = FullParalysisChanceEffect(kind="full_paralysis_chance", payload=ChancePayload(chance=25))

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    with patch("random.random", return_value=0.10):  # 10% < 25% chance
        strategy.apply(context, execution)

    assert context.get_action_block_reason("inst_1") == "full_paralysis_chance"
    assert len(context.events) == 1
    assert context.events[0].kind == "action_skipped"


def test_paralysis_does_not_block_move(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="paralyze", name="Paralyze", category="major", effects=[])
    effect = FullParalysisChanceEffect(kind="full_paralysis_chance", payload=ChancePayload(chance=25))

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    with patch("random.random", return_value=0.50):  # 50% > 25% chance
        strategy.apply(context, execution)

    assert context.get_action_block_reason("inst_1") is None
    assert len(context.events) == 0
