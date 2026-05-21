import pytest
import math

from puchamon.modules.battle.domain.strategies.conditions.physical_attack_modifier_condition_effect_strategy import (
    PhysicalAttackModifierConditionEffectStrategy,
)
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import PhysicalAttackModifierEffect, MultiplierPayload, Condition
from puchamon.modules.pokedex.domain.entities import Movement
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, Player


def _build_base_instance() -> BattleInstance:
    return BattleInstance.model_construct(
        id="inst_1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="charmander",
        moveset_id="m1",
        types=["fire"],
        current_hp=100,
        max_hp=100,
        status="burn",
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return PhysicalAttackModifierConditionEffectStrategy()


def test_physical_attack_modified(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    context.transient["current_damage"] = 100

    condition = Condition.model_construct(id="burn", name="Burn", category="major", effects=[])
    effect = PhysicalAttackModifierEffect(kind="physical_attack_modifier", payload=MultiplierPayload(multiplier=0.5))
    movement = Movement.model_construct(id="scratch", name="Scratch", category="physical", type="normal", accuracy=100, pp=35, target="any_adjacent")

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1", movement=movement)

    strategy.apply(context, execution)

    assert context.transient["current_damage"] == 50


def test_special_attack_not_modified(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    context.transient["current_damage"] = 100

    condition = Condition.model_construct(id="burn", name="Burn", category="major", effects=[])
    effect = PhysicalAttackModifierEffect(kind="physical_attack_modifier", payload=MultiplierPayload(multiplier=0.5))
    movement = Movement.model_construct(id="ember", name="Ember", category="special", type="fire", accuracy=100, pp=25, target="any_adjacent")

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1", movement=movement)

    strategy.apply(context, execution)

    assert context.transient["current_damage"] == 100
