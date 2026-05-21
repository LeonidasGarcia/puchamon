import pytest
from puchamon.modules.battle.domain.strategies.conditions.speed_modifier_condition_effect_strategy import SpeedModifierConditionEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import Condition, SpeedModifierEffect, MultiplierPayload
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle


def _build_base_instance(instance_id="inst_1") -> BattleInstance:
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="pikachu",
        moveset_id="m1",
        types=["electric"],
        current_hp=100,
        max_hp=100,
        status=None,
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return SpeedModifierConditionEffectStrategy()


def test_speed_modifier_successfully(strategy):
    target = _build_base_instance()
    battle = Battle.model_construct(id="b1", turn=1)
    # Transient dict should already have current_speed
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})
    context.transient["current_speed"] = 100

    condition = Condition.model_construct(id="paralyze", name="Paralysis")
    # Reduce speed to 25% (Gen 6+ is 50%, Gen 1-5 is 25%)
    effect = SpeedModifierEffect(kind="speed_modifier", payload=MultiplierPayload(multiplier=0.25))
    
    execution = ConditionEffectExecutionInput(
        condition=condition,
        effect=effect,
        holder_instance_id=target.id,
    )

    strategy.apply(context, execution)

    assert context.transient["current_speed"] == 25


def test_speed_modifier_multiple_modifiers(strategy):
    target = _build_base_instance()
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})
    context.transient["current_speed"] = 100

    condition = Condition.model_construct(id="some_condition", name="Some Condition")
    effect = SpeedModifierEffect(kind="speed_modifier", payload=MultiplierPayload(multiplier=0.5))
    
    execution = ConditionEffectExecutionInput(
        condition=condition,
        effect=effect,
        holder_instance_id=target.id,
    )

    # Apply once
    strategy.apply(context, execution)
    assert context.transient["current_speed"] == 50

    # Apply again (simulating multiple conditions)
    strategy.apply(context, execution)
    assert context.transient["current_speed"] == 25
