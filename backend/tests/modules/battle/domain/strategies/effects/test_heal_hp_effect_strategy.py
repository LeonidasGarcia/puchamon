import pytest
from puchamon.modules.battle.domain.strategies.effects.heal_hp_effect_strategy import HealHpEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, MoveEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.effects import MoveEffect, HealPayload
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle
from puchamon.modules.battle.domain.entities import BattleStats


def _build_base_instance(instance_id="inst_1", current_hp=50, max_hp=100) -> BattleInstance:
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="pikachu",
        moveset_id="m1",
        types=["electric"],
        current_hp=current_hp,
        max_hp=max_hp,
        stats=BattleStats(hp=max_hp, atk=100, def_=100, spa=100, spd=100, spe=100),
        status=None,
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return HealHpEffectStrategy()


def test_heal_hp_successfully(strategy):
    target = _build_base_instance(current_hp=40, max_hp=100)
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    # Heal 50% of max HP
    effect = MoveEffect.model_construct(id="eff_heal", kind="heal_hp", payload=HealPayload(ratio=0.5))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.current_hp == 90
    assert len(context.events) == 1
    assert context.events[0].kind == "heal_hp"
    assert context.events[0].payload["value"] == 50


def test_heal_hp_caps_at_max_hp(strategy):
    target = _build_base_instance(current_hp=80, max_hp=100)
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    # Heal 50% of max HP (50 HP), but only 20 HP needed
    effect = MoveEffect.model_construct(id="eff_heal", kind="heal_hp", payload=HealPayload(ratio=0.5))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.current_hp == 100
    assert len(context.events) == 1
    assert context.events[0].kind == "heal_hp"
    assert context.events[0].payload["value"] == 20


def test_heal_hp_skips_fainted_target(strategy):
    target = _build_base_instance(current_hp=0, max_hp=100)
    target.fainted = True
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_heal", kind="heal_hp", payload=HealPayload(ratio=0.5))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.current_hp == 0
    assert len(context.events) == 0
