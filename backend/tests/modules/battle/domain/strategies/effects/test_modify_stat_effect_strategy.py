import pytest
from puchamon.modules.battle.domain.strategies.effects.modify_stat_effect_strategy import ModifyStatEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, MoveEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.effects import MoveEffect, ModifyStatPayload, StatChange
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle
from puchamon.modules.battle.domain.entities import StatStages


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
        stages=StatStages(),
        status=None,
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return ModifyStatEffectStrategy()


def test_modify_stat_successfully(strategy):
    target = _build_base_instance()
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    # Raise Attack by 1 stage
    effect = MoveEffect.model_construct(
        id="eff_bulk_up",
        kind="modify_stat",
        payload=ModifyStatPayload(changes=[StatChange(stat="atk", stages=1)]),
    )
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.stages.atk == 1
    assert len(context.events) == 1
    assert context.events[0].kind == "stat_changed"
    assert "rose" in context.events[0].message


def test_modify_stat_sharp_rise(strategy):
    target = _build_base_instance()
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    # Raise SpA by 2 stages
    effect = MoveEffect.model_construct(
        id="eff_nasty_plot",
        kind="modify_stat",
        payload=ModifyStatPayload(changes=[StatChange(stat="spa", stages=2)]),
    )
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.stages.spa == 2
    assert "rose sharply" in context.events[0].message


def test_modify_stat_caps_at_max(strategy):
    target = _build_base_instance()
    target.stages.atk = 5
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    # Try to raise Attack by 2 stages (should cap at 6)
    effect = MoveEffect.model_construct(
        id="eff_swords_dance",
        kind="modify_stat",
        payload=ModifyStatPayload(changes=[StatChange(stat="atk", stages=2)]),
    )
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.stages.atk == 6
    assert context.events[0].kind == "stat_changed"


def test_modify_stat_fails_at_limit(strategy):
    target = _build_base_instance()
    target.stages.atk = 6
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    # Try to raise Attack further
    effect = MoveEffect.model_construct(
        id="eff_swords_dance",
        kind="modify_stat",
        payload=ModifyStatPayload(changes=[StatChange(stat="atk", stages=1)]),
    )
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.stages.atk == 6
    assert context.events[0].kind == "stat_change_failed"
    assert "won't go any higher" in context.events[0].message


def test_modify_stat_multiple_changes(strategy):
    target = _build_base_instance()
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    # Shell Smash: Atk+2, SpA+2, Spe+2, Def-1, SpD-1
    effect = MoveEffect.model_construct(
        id="eff_shell_smash",
        kind="modify_stat",
        payload=ModifyStatPayload(
            changes=[
                StatChange(stat="atk", stages=2),
                StatChange(stat="spa", stages=2),
                StatChange(stat="spe", stages=2),
                StatChange(stat="def", stages=-1),
                StatChange(stat="spd", stages=-1),
            ]
        ),
    )
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.stages.atk == 2
    assert target.stages.spa == 2
    assert target.stages.spe == 2
    assert target.stages.def_ == -1
    assert target.stages.spd == -1
    assert len(context.events) == 5
