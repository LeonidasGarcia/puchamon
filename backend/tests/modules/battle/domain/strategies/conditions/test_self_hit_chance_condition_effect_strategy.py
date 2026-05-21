import pytest
from unittest.mock import patch

from puchamon.modules.battle.domain.strategies.conditions.self_hit_chance_condition_effect_strategy import SelfHitChanceConditionEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import SelfHitChanceEffect, ChancePayload, Condition
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
        level=50,
        current_hp=100,
        max_hp=100,
        fainted=False,
        volatile_status=["confusion"],
    )


@pytest.fixture
def strategy():
    return SelfHitChanceConditionEffectStrategy()


def test_confusion_hits_self(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="confusion", name="Confusion", category="volatile", effects=[])
    effect = SelfHitChanceEffect(kind="self_hit_chance", payload=ChancePayload(chance=33))

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    with patch("random.random", return_value=0.10):  # 10% < 33% chance
        strategy.apply(context, execution)

    assert context.get_action_block_reason("inst_1") == "self_hit_chance"
    events = [e for e in context.events if e.kind == "action_skipped"]
    assert len(events) == 1
    assert "hurt itself" in events[0].message

    damage_events = [e for e in context.events if e.kind == "condition_damage"]
    assert len(damage_events) == 1
    assert instance.current_hp < 100


def test_confusion_does_not_hit_self(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="confusion", name="Confusion", category="volatile", effects=[])
    effect = SelfHitChanceEffect(kind="self_hit_chance", payload=ChancePayload(chance=33))

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    with patch("random.random", return_value=0.50):  # 50% > 33% chance
        strategy.apply(context, execution)

    assert context.get_action_block_reason("inst_1") is None
    events = [e for e in context.events if e.kind == "condition_message"]
    assert len(events) == 1
    assert "is confused!" in events[0].message
    assert instance.current_hp == 100
