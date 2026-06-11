"""Minimax algorithm with Alpha-Beta pruning for AI decision making."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...battle.domain.entities import Battle, BattleInstance
from ...pokedex.domain.entities import MoveEffect, Movement
from .action_utils import get_available_actions, get_opponent_trainer_id
from .state_simulator import simulate_state_transition

if TYPE_CHECKING:
    from ...pokedex.domain.entities import Type

HeuristicFunction = Callable[..., float]
MIN_REQUIRED_SIDES = 2


@dataclass(slots=True)
class MinimaxMetrics:
    """Search counters collected during one Minimax decision."""

    nodes_visited: int = 0
    pruned_branches: int = 0


def is_terminal_state(battle: Battle, instances: dict[str, BattleInstance]) -> bool:
    """Return True when the battle has ended or a side has no usable team members."""
    if battle.status == "finished" or battle.result is not None:
        return True

    if len(battle.sides) < MIN_REQUIRED_SIDES:
        return True

    for trainer_id in battle.sides:
        has_available_instance = any(
            instance.trainer_id == trainer_id and not instance.fainted and instance.current_hp > 0 for instance in instances.values()
        )
        if not has_available_instance:
            return True
    return False


def _evaluate_leaf(  # noqa: PLR0913
    heuristic_func: HeuristicFunction,
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    movements: Mapping[str, Movement] | None,
    type_chart: Mapping[str, "Type"] | None,
    move_effects: Mapping[str, MoveEffect] | None,
) -> float:
    return heuristic_func(battle, instances, player_trainer_id, movements=movements, type_chart=type_chart, move_effects=move_effects)


def minimax(  # noqa: PLR0913
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    depth: int,
    alpha: float,
    beta: float,
    is_maximizing_player: bool,
    heuristic_func: HeuristicFunction,
    movements: Mapping[str, Movement] | None = None,
    type_chart: Mapping[str, "Type"] | None = None,
    move_effects: Mapping[str, MoveEffect] | None = None,
    metrics: MinimaxMetrics | None = None,
) -> float:
    """Minimax algorithm with Alpha-Beta pruning.

    Args:
        battle: The current battle state.
        instances: The battle instances.
        player_trainer_id: The AI player's trainer ID.
        depth: Remaining search depth.
        alpha: Alpha value for pruning.
        beta: Beta value for pruning.
        is_maximizing_player: True if maximizing player's turn.
        heuristic_func: Heuristic function to evaluate leaf nodes.
        movements: Dict of Movement entities.
        type_chart: Optional type chart used by proactive heuristics.
        metrics: Optional counters for visited nodes and alpha-beta cutoffs.

    Returns:
        The evaluated score for this branch.
    """
    if metrics is not None:
        metrics.nodes_visited += 1

    if depth <= 0 or is_terminal_state(battle, instances):
        return _evaluate_leaf(heuristic_func, battle, instances, player_trainer_id, movements, type_chart, move_effects)

    opponent_trainer_id = get_opponent_trainer_id(battle, player_trainer_id)
    if opponent_trainer_id is None:
        return _evaluate_leaf(heuristic_func, battle, instances, player_trainer_id, movements, type_chart, move_effects)

    acting_trainer_id = player_trainer_id if is_maximizing_player else opponent_trainer_id
    opposing_trainer_id = opponent_trainer_id if is_maximizing_player else player_trainer_id
    actions = get_available_actions(battle, instances, acting_trainer_id)

    if not actions:
        return _evaluate_leaf(heuristic_func, battle, instances, player_trainer_id, movements, type_chart, move_effects)

    if is_maximizing_player:
        max_eval = float("-inf")
        for action in actions:
            next_battle, next_instances = simulate_state_transition(
                battle,
                instances,
                action,
                acting_trainer_id,
                opposing_trainer_id,
                movements,
                type_chart,
                move_effects,
            )
            eval_score = minimax(
                next_battle,
                next_instances,
                player_trainer_id,
                depth - 1,
                alpha,
                beta,
                False,
                heuristic_func,
                movements,
                type_chart,
                move_effects,
                metrics,
            )
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                if metrics is not None:
                    metrics.pruned_branches += 1
                break
        return max_eval

    min_eval = float("inf")
    for action in actions:
        next_battle, next_instances = simulate_state_transition(
            battle,
            instances,
            action,
            acting_trainer_id,
            opposing_trainer_id,
            movements,
            type_chart,
            move_effects,
        )
        eval_score = minimax(
            next_battle,
            next_instances,
            player_trainer_id,
            depth - 1,
            alpha,
            beta,
            True,
            heuristic_func,
            movements,
            type_chart,
            move_effects,
            metrics,
        )
        min_eval = min(min_eval, eval_score)
        beta = min(beta, eval_score)
        if beta <= alpha:
            if metrics is not None:
                metrics.pruned_branches += 1
            break
    return min_eval
