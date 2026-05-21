import pytest
from unittest.mock import patch

from puchamon.modules.battle.domain.strategies.effects.apply_major_status_effect_strategy import ApplyMajorStatusEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, MoveEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.effects import MoveEffect, StatusPayload
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, Player


def _build_base_instance(pokemon_id="pikachu", types=None) -> BattleInstance:
    if types is None:
        types = ["electric"]
    return BattleInstance.model_construct(
        id=f"inst_{pokemon_id}",
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
    return ApplyMajorStatusEffectStrategy()


def test_apply_status_successfully(strategy):
    target = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[]),
        side_2=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=[target.id])]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_paralyze", kind="apply_major_status", payload=StatusPayload(condition_id="paralyze"))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.status == "paralyze"
    assert len(context.events) == 1
    assert context.events[0].kind == "status_applied"


def test_apply_status_fails_if_already_statused(strategy):
    target = _build_base_instance()
    target.status = "burn"  # Already statused

    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[]),
        side_2=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=[target.id])]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_paralyze", kind="apply_major_status", payload=StatusPayload(condition_id="paralyze"))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.status == "burn"  # Should not be overwritten
    assert len(context.events) == 0


def test_apply_status_fails_if_immune(strategy):
    target = _build_base_instance(pokemon_id="charmander", types=["fire"])

    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[]),
        side_2=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=[target.id])]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    effect = MoveEffect.model_construct(id="eff_burn", kind="apply_major_status", payload=StatusPayload(condition_id="burn"))
    execution = MoveEffectExecutionInput(effect=effect, source_instance_id="some_source", target_instance_ids=[target.id])

    strategy.apply(context, execution)

    assert target.status is None  # Immune to burn
    assert len(context.events) == 1
    assert context.events[0].kind == "status_failed_immune"
