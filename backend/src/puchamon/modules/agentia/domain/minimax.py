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


def _action_sort_key(
    action: tuple[str, str],
    movements: Mapping[str, Movement],
) -> int:
    """Return a sort key so that damaging moves come first (best for alpha-beta)."""
    if action[0] == "MOVE":
        move = movements.get(action[1])
        if move and move.power:
            return -move.power
    return 0


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
        return heuristic_func(battle, instances, player_trainer_id, movements=movements, type_chart=type_chart, move_effects=move_effects)

    opponent_trainer_id = get_opponent_trainer_id(battle, player_trainer_id)
    if opponent_trainer_id is None:
        return heuristic_func(battle, instances, player_trainer_id, movements=movements, type_chart=type_chart, move_effects=move_effects)

    acting_trainer_id = player_trainer_id if is_maximizing_player else opponent_trainer_id
    opposing_trainer_id = opponent_trainer_id if is_maximizing_player else player_trainer_id
    actions = get_available_actions(battle, instances, acting_trainer_id)
    if movements is not None:
        actions.sort(key=lambda a: _action_sort_key(a, movements))

    if not actions:
        return heuristic_func(battle, instances, player_trainer_id, movements=movements, type_chart=type_chart, move_effects=move_effects)

    best_score = float("-inf") if is_maximizing_player else float("inf")

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
            not is_maximizing_player,
            heuristic_func,
            movements,
            type_chart,
            move_effects,
            metrics,
        )

        if is_maximizing_player:
            best_score = max(best_score, eval_score)
            alpha = max(alpha, eval_score)
        else:
            best_score = min(best_score, eval_score)
            beta = min(beta, eval_score)

        if beta <= alpha:
            if metrics is not None:
                metrics.pruned_branches += 1
            break

    return best_score
