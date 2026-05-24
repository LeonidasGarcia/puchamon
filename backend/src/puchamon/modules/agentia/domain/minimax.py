"""Minimax algorithm with Alpha-Beta pruning for AI decision making."""

import copy
from collections.abc import Callable

from ...battle.domain.entities import Battle, BattleInstance
from .action_utils import get_available_actions, get_opponent_trainer_id
from .state_simulator import simulate_action


def minimax(
    battle: Battle,
    instances: dict[str, BattleInstance],
    player_trainer_id: str,
    depth: int,
    alpha: float,
    beta: float,
    maximizing: bool,
    heuristic_func: Callable[[Battle, dict[str, BattleInstance], str], float],
    movements: dict | None = None,
) -> float:
    """Minimax algorithm with Alpha-Beta pruning.

    Args:
        battle: The current battle state.
        instances: The battle instances.
        player_trainer_id: The AI player's trainer ID.
        depth: Remaining search depth.
        alpha: Alpha value for pruning.
        beta: Beta value for pruning.
        maximizing: True if maximizing player's turn.
        heuristic_func: Heuristic function to evaluate leaf nodes.
        movements: Dict of Movement entities.

    Returns:
        The evaluated score for this branch.
    """
    if depth == 0:
        return heuristic_func(battle, instances, player_trainer_id)

    opponent_trainer_id = get_opponent_trainer_id(battle, player_trainer_id)
    if opponent_trainer_id is None:
        return heuristic_func(battle, instances, player_trainer_id)

    current_id = player_trainer_id if maximizing else opponent_trainer_id
    actions = get_available_actions(battle, instances, current_id)

    if not actions:
        return heuristic_func(battle, instances, player_trainer_id)

    if maximizing:
        max_eval = float("-inf")
        for action in actions:
            state_copy = simulate_action(
                copy.deepcopy(battle),
                copy.deepcopy(instances),
                action,
                player_trainer_id,
                opponent_trainer_id,
                movements,
            )
            eval_score = minimax(
                state_copy[0],
                state_copy[1],
                player_trainer_id,
                depth - 1,
                alpha,
                beta,
                False,
                heuristic_func,
                movements,
            )
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for action in actions:
            state_copy = simulate_action(
                copy.deepcopy(battle),
                copy.deepcopy(instances),
                action,
                player_trainer_id,
                opponent_trainer_id,
                movements,
            )
            eval_score = minimax(
                state_copy[0],
                state_copy[1],
                player_trainer_id,
                depth - 1,
                alpha,
                beta,
                True,
                heuristic_func,
                movements,
            )
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval
