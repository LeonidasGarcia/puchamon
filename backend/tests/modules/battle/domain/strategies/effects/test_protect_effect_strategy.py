"""Tests for the Protect move effect strategy."""

from unittest.mock import patch

import pytest

from puchamon.modules.battle.domain.entities.battle import Battle
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, MoveEffectExecutionInput
from puchamon.modules.battle.domain.strategies.effects.protect_effect_strategy import ProtectEffectStrategy
from puchamon.modules.pokedex.domain.entities.effects import MoveEffect, ProtectPayload


def _build_base_instance(instance_id: str = "inst_1") -> BattleInstance:
    """Build a base battle instance for testing."""
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
def strategy() -> ProtectEffectStrategy:
    """Fixture for the ProtectEffectStrategy."""
    return ProtectEffectStrategy()


def test_protect_successfully_first_turn(strategy: ProtectEffectStrategy) -> None:
    """Verify Protect succeeds on the first turn."""
    source = _build_base_instance()
    battle_turn = 1
    battle = Battle.model_construct(id="b1", turn=battle_turn)
    instance_id = str(source.id)
    context = BattleStrategyContext(battle=battle, battle_instances={instance_id: source})

    effect = MoveEffect.model_construct(id="eff_protect", kind="protect", payload=ProtectPayload(duration=1))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id=instance_id, target_instance_ids=[instance_id])

    with patch("random.random", return_value=0.5):  # Roll 0.5, success_chance 1.0
        strategy.apply(context, execution)

    assert "protect" in source.volatile_status
    assert source.turn_counters["protect"] == 1
    assert source.turn_counters["_protect_last_turn"] == battle_turn
    assert len(context.events) == 1
    assert context.events[0].kind == "status_applied"


def test_protect_consecutive_use_success_chance(strategy: ProtectEffectStrategy) -> None:
    """Verify Protect success/failure probability on consecutive uses."""
    # Second use (consecutive=2) has 50% success chance
    source = _build_base_instance()
    source.turn_counters = {"protect": 1, "_protect_last_turn": 1}
    battle_turn = 2
    battle = Battle.model_construct(id="b1", turn=battle_turn)
    instance_id = str(source.id)
    context = BattleStrategyContext(battle=battle, battle_instances={instance_id: source})

    effect = MoveEffect.model_construct(id="eff_protect", kind="protect", payload=ProtectPayload(duration=1))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id=instance_id, target_instance_ids=[instance_id])

    # Case: Success (roll 0.4 < 0.5)
    expected_consecutive = 2
    with patch("random.random", return_value=0.4):
        strategy.apply(context, execution)
    assert "protect" in source.volatile_status
    assert source.turn_counters["protect"] == expected_consecutive

    # Case: Failure (roll 0.6 >= 0.5)
    source.volatile_status = []
    source.turn_counters = {"protect": 1, "_protect_last_turn": 1}
    with patch("random.random", return_value=0.6):
        strategy.apply(context, execution)
    assert "protect" not in source.volatile_status
    assert source.turn_counters["protect"] == 0


def test_protect_fourth_use_always_fails(strategy: ProtectEffectStrategy) -> None:
    """Verify Protect fails automatically on the fourth consecutive use."""
    # Fourth use (consecutive=4) has 0% success chance
    source = _build_base_instance()
    source.turn_counters = {"protect": 3, "_protect_last_turn": 3}
    battle_turn = 4
    battle = Battle.model_construct(id="b1", turn=battle_turn)
    instance_id = str(source.id)
    context = BattleStrategyContext(battle=battle, battle_instances={instance_id: source})

    effect = MoveEffect.model_construct(id="eff_protect", kind="protect", payload=ProtectPayload(duration=1))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id=instance_id, target_instance_ids=[instance_id])

    with patch("random.random", return_value=0.0):  # Even with a perfect roll
        strategy.apply(context, execution)

    assert "protect" not in source.volatile_status
    assert source.turn_counters["protect"] == 0


def test_protect_reset_after_gap(strategy: ProtectEffectStrategy) -> None:
    """Verify Protect success rate resets after a gap in usage."""
    source = _build_base_instance()
    source.turn_counters = {"protect": 1, "_protect_last_turn": 1}
    battle_turn = 3
    battle = Battle.model_construct(id="b1", turn=battle_turn)  # Gap of one turn
    instance_id = str(source.id)
    context = BattleStrategyContext(battle=battle, battle_instances={instance_id: source})

    effect = MoveEffect.model_construct(id="eff_protect", kind="protect", payload=ProtectPayload(duration=1))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id=instance_id, target_instance_ids=[instance_id])

    # consecutive should be 1, success_chance 1.0
    with patch("random.random", return_value=0.9):
        strategy.apply(context, execution)

    assert "protect" in source.volatile_status
    assert source.turn_counters["protect"] == 1
    assert source.turn_counters["_protect_last_turn"] == battle_turn
