import pytest
from puchamon.modules.battle.domain.strategies.effects.apply_volatile_status_effect_strategy import ApplyVolatileStatusEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, MoveEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.effects import MoveEffect, StatusPayload
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState


def _build_base_instance(instance_id="inst_1", pokemon_id="pikachu", types=None) -> BattleInstance:
    if types is None:
        types = ["electric"]
    return BattleInstance.model_construct(
        id=instance_id,
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id=pokemon_id,
        moveset_id="m1",
        types=types,
        current_hp=100,
        max_hp=100,
        status=None,
        fainted=False,
        volatile_status=[],
    )


@pytest.fixture
def strategy():
    return ApplyVolatileStatusEffectStrategy()


def test_apply_volatile_status_successfully(strategy):
    target = _build_base_instance()
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_confuse", kind="apply_volatile_status", payload=StatusPayload(condition_id="confusion"))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert "confusion" in target.volatile_status
    assert len(context.events) == 1
    assert context.events[0].kind == "volatile_status_applied"


def test_apply_volatile_status_fails_if_already_present(strategy):
    target = _build_base_instance()
    target.volatile_status = ["confusion"]

    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_confuse", kind="apply_volatile_status", payload=StatusPayload(condition_id="confusion"))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.volatile_status == ["confusion"]
    assert len(context.events) == 0


def test_apply_volatile_status_fails_if_immune(strategy):
    target = _build_base_instance(pokemon_id="bulbasaur", types=["grass", "poison"])

    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_leech_seed", kind="apply_volatile_status", payload=StatusPayload(condition_id="seeded"))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert "seeded" not in target.volatile_status
    assert len(context.events) == 1
    assert context.events[0].kind == "volatile_status_failed_immune"


def test_apply_volatile_status_skips_fainted_target(strategy):
    target = _build_base_instance()
    target.current_hp = 0
    target.fainted = True

    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_confuse", kind="apply_volatile_status", payload=StatusPayload(condition_id="confusion"))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert "confusion" not in target.volatile_status
    assert len(context.events) == 0
