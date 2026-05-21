import pytest
from unittest.mock import patch
from puchamon.modules.battle.domain.strategies.effects.protect_effect_strategy import ProtectEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, MoveEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.effects import MoveEffect, ProtectPayload
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
        turn_counters={},
    )


@pytest.fixture
def strategy():
    return ProtectEffectStrategy()


def test_protect_successfully_first_turn(strategy):
    source = _build_base_instance()
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={source.id: source})

    effect = MoveEffect.model_construct(id="eff_protect", kind="protect", payload=ProtectPayload(duration=1))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id=source.id, target_instance_ids=[source.id])

    with patch("random.random", return_value=0.5):  # Roll 0.5, miss_chance 0.0
        strategy.apply(context, execution)

    assert "protect" in source.volatile_status
    assert source.turn_counters["protect"] == 1
    assert source.turn_counters["_protect_last_turn"] == 1
    assert len(context.events) == 1
    assert context.events[0].kind == "status_applied"


def test_protect_consecutive_use_fails(strategy):
    source = _build_base_instance()
    source.turn_counters = {"protect": 1, "_protect_last_turn": 1}
    battle = Battle.model_construct(id="b1", turn=2)
    context = BattleStrategyContext(battle=battle, battle_instances={source.id: source})

    effect = MoveEffect.model_construct(id="eff_protect", kind="protect", payload=ProtectPayload(duration=1))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id=source.id, target_instance_ids=[source.id])

    # miss_chance = (2-1) * 0.33 = 0.33
    with patch("random.random", return_value=0.1):  # Roll 0.1 < 0.33, should fail
        strategy.apply(context, execution)

    assert "protect" not in source.volatile_status
    assert source.turn_counters["protect"] == 0
    assert len(context.events) == 1
    assert context.events[0].kind == "move_failed"


def test_protect_reset_after_gap(strategy):
    source = _build_base_instance()
    source.turn_counters = {"protect": 1, "_protect_last_turn": 1}
    battle = Battle.model_construct(id="b1", turn=3)  # Gap of one turn
    context = BattleStrategyContext(battle=battle, battle_instances={source.id: source})

    effect = MoveEffect.model_construct(id="eff_protect", kind="protect", payload=ProtectPayload(duration=1))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id=source.id, target_instance_ids=[source.id])

    # consecutive should be 1, miss_chance 0.0
    with patch("random.random", return_value=0.9):
        strategy.apply(context, execution)

    assert "protect" in source.volatile_status
    assert source.turn_counters["protect"] == 1
    assert source.turn_counters["_protect_last_turn"] == 3
