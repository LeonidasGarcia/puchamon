import pytest

from puchamon.modules.battle.domain.strategies.conditions.bad_poison_condition_effect_strategy import BadPoisonConditionEffectStrategy
from puchamon.modules.battle.domain.runtime.context import BattleStrategyContext, ConditionEffectExecutionInput
from puchamon.modules.pokedex.domain.entities.conditions import BadPoisonEffect, BadPoisonPayload, Condition
from puchamon.modules.battle.domain.entities.battle_instance import BattleInstance
from puchamon.modules.battle.domain.entities.battle import Battle, SideState, Player


def _build_base_instance() -> BattleInstance:
    return BattleInstance.model_construct(
        id="inst_1",
        battle_id="b1",
        trainer_id="t1",
        slot=0,
        pokemon_id="bulbasaur",
        moveset_id="m1",
        types=["poison"],
        current_hp=100,
        max_hp=100,
        status="bad_poison",
        fainted=False,
        volatile_status=[],
        turn_counters={"bad_poison": 3},
    )


@pytest.fixture
def strategy():
    return BadPoisonConditionEffectStrategy()


def test_bad_poison_scaling_damage(strategy):
    instance = _build_base_instance()
    battle = Battle.model_construct(
        id="b1",
        format="singles",
        side_1=SideState.model_construct(players=[Player.model_construct(id="t1", instance_ids=["inst_1"])]),
        side_2=SideState.model_construct(players=[]),
        turn=1,
    )
    context = BattleStrategyContext(battle=battle, battle_instances={"inst_1": instance})
    condition = Condition.model_construct(id="bad_poison", name="Bad Poison", category="major", effects=[])
    effect = BadPoisonEffect(kind="end_turn_bad_poison_damage", payload=BadPoisonPayload(base_ratio=0.0625))  # 1/16

    execution = ConditionEffectExecutionInput(condition=condition, effect=effect, holder_instance_id="inst_1")

    strategy.apply(context, execution)

    # 3 turns * 1/16 = 3/16 = 0.1875
    # 100 * 0.1875 = 18.75 -> 18 damage
    assert instance.current_hp == 100 - 18
