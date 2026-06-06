import pytest

from puchamon.modules.battle.domain.strategies.conditions.cannot_move_condition_effect_strategy import CannotMoveConditionEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import CannotMoveEffect, EmptyPayload, Condition
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, Player


def _build_base_instance() -> BattleInstance:
    return BattleInstance.model_construct(
        id="inst_1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="squirtle",
        moveset_id="m1",
        types=["water"],
        current_hp=100,
        max_hp=100,
        fainted=False,
        volatile_status=["flinch"],
    )


@pytest.fixture
def strategy():
    return CannotMoveConditionEffectStrategy()


def test_cannot_move_blocks_action(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="flinch", name="Flinch", category="volatile", effects=[])
    effect = CannotMoveEffect(kind="cannot_move", payload=EmptyPayload())

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    strategy.apply(context, execution)

    assert context.get_action_block_reason("inst_1") == "cannot_move"
    assert len(context.events) == 1
    assert context.events[0].kind == "action_skipped"
    assert "retrocedió" in context.events[0].message
