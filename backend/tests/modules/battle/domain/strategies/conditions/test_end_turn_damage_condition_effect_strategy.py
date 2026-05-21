import pytest
from puchamon.modules.battle.domain.strategies.conditions.end_turn_damage_condition_effect_strategy import EndTurnDamageConditionEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import Condition, EndTurnDamageEffect, RatioPayload
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState


def _build_base_instance(instance_id="inst_1", current_hp=100, max_hp=100, trainer_id="t1") -> BattleInstance:
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id=trainer_id,
        slot=0,
        pokemon_id="pikachu",
        moveset_id="m1",
        types=["electric"],
        current_hp=current_hp,
        max_hp=max_hp,
        status=None,
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return EndTurnDamageConditionEffectStrategy()


def test_end_turn_damage_successfully(strategy):
    target = _build_base_instance(current_hp=100, max_hp=100)
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    condition = Condition.model_construct(id="poison", name="Poison")
    # 1/8 of max HP damage (12.5 HP -> 12 HP)
    effect = EndTurnDamageEffect(kind="end_turn_damage", payload=RatioPayload(ratio=0.125))
    
    execution = ConditionEffectExecutionInput(
        condition=condition,
        effect=effect,
        holder_instance_id=target.id,
    )

    strategy.apply(context, execution)

    assert target.current_hp == 88
    assert len(context.events) == 1
    assert context.events[0].kind == "condition_damage"
    assert context.events[0].payload["value"] == 12


def test_end_turn_damage_faints_target(strategy):
    target = _build_base_instance(current_hp=10, max_hp=100, trainer_id="t1")
    battle = Battle.model_construct(
        id="b1",
        turn=1,
        sides={
            "t1": SideState.model_construct(active_pokemon_instance_ids=[target.id]),
        }
    )
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    condition = Condition.model_construct(id="poison", name="Poison")
    effect = EndTurnDamageEffect(kind="end_turn_damage", payload=RatioPayload(ratio=0.125))
    
    execution = ConditionEffectExecutionInput(
        condition=condition,
        effect=effect,
        holder_instance_id=target.id,
    )

    strategy.apply(context, execution)

    assert target.current_hp == 0
    assert target.fainted is True
    assert any(e.kind == "pokemon_fainted" for e in context.events)
