import pytest
from puchamon.modules.battle.domain.strategies.conditions.block_protectable_moves_condition_effect_strategy import BlockProtectableMovesConditionEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import Condition, BlockProtectableMovesEffect, EmptyPayload
from puchamon.modules.pokedex.domain.entities.movements import Movement
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
    return BlockProtectableMovesConditionEffectStrategy()


def test_block_protectable_move_successfully(strategy):
    target = _build_base_instance()
    target.volatile_status = ["protect"]
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    movement = Movement.model_construct(id="tackle", name="Tackle", protectable=True)
    condition = Condition.model_construct(id="c_protect", name="Protect")
    effect = BlockProtectableMovesEffect(kind="block_protectable_moves", payload=EmptyPayload())
    
    execution = ConditionEffectExecutionInput(
        condition=condition,
        effect=effect,
        holder_instance_id=target.id,
        source_instance_id="attacker_id",
        movement=movement,
    )

    strategy.apply(context, execution)

    assert target.id in context.transient["blocked_targets"]
    assert len(context.events) == 1
    assert context.events[0].kind == "move_blocked"


def test_allow_non_protectable_move(strategy):
    target = _build_base_instance()
    target.volatile_status = ["protect"]
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    movement = Movement.model_construct(id="feint", name="Feint", protectable=False)
    condition = Condition.model_construct(id="c_protect", name="Protect")
    effect = BlockProtectableMovesEffect(kind="block_protectable_moves", payload=EmptyPayload())
    
    execution = ConditionEffectExecutionInput(
        condition=condition,
        effect=effect,
        holder_instance_id=target.id,
        source_instance_id="attacker_id",
        movement=movement,
    )

    strategy.apply(context, execution)

    assert "blocked_targets" not in context.transient
    assert len(context.events) == 0


def test_allow_move_if_protect_not_active(strategy):
    target = _build_base_instance()
    target.volatile_status = []  # No protect
    battle = Battle.model_construct(id="b1", turn=1)
    context = BattleStrategyContext(battle=battle, battle_instances={target.id: target})

    movement = Movement.model_construct(id="tackle", name="Tackle", protectable=True)
    condition = Condition.model_construct(id="c_protect", name="Protect")
    effect = BlockProtectableMovesEffect(kind="block_protectable_moves", payload=EmptyPayload())
    
    execution = ConditionEffectExecutionInput(
        condition=condition,
        effect=effect,
        holder_instance_id=target.id,
        source_instance_id="attacker_id",
        movement=movement,
    )

    strategy.apply(context, execution)

    assert "blocked_targets" not in context.transient
    assert len(context.events) == 0
