"""Action selection strategies for AI."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from secrets import choice
from typing import Literal

from ....shared.infrastructure.config import settings
from ...battle.domain.entities import Battle, BattleInstance
from ...pokedex.domain.entities import Movement, Type
from .action_utils import get_available_actions, get_opponent_trainer_id
from .heuristics import evaluate_level_2, evaluate_level_3_ga, evaluate_level_3_manual, evaluate_level_3_weighted
from .minimax import MinimaxMetrics, minimax
from .state_simulator import simulate_state_transition

Action = tuple[str, str]

AIDifficultyLevel = Literal[1, 2, 3, 4]
AI_LEVEL_EASY = 1
AI_LEVEL_MEDIUM = 2
AI_LEVEL_HARD_MANUAL = 3
AI_LEVEL_HARD_GA = 4

DEFAULT_MINIMAX_DEPTH = settings.MINIMAX_DEPTH


class ActionSelector(ABC):
    """Abstract base class for action selection strategies."""

    @abstractmethod
    def select(  # noqa: PLR0913
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
        movements: Mapping[str, Movement] | None = None,
        type_chart: Mapping[str, Type] | None = None,
        metrics: MinimaxMetrics | None = None,
    ) -> Action | None:
        """Select an action (move or switch) from available options.

        Args:
            battle: The current battle state.
            instances: Dict of battle instances keyed by ID.
            trainer_id: The trainer ID of the AI player.
            movements: Dict of Movement entities keyed by ID.

        Returns:
            Action tuple (action_type, action_id) or None if no action available.
            action_type is "MOVE" or "SWITCH".
            action_id is move_id or instance_id respectively.
        """
        pass


class RandomActionSelector(ActionSelector):
    """Select action randomly (Level 1 - Easy)."""

    def select(  # noqa: PLR0913
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
        movements: Mapping[str, Movement] | None = None,
        type_chart: Mapping[str, Type] | None = None,
        metrics: MinimaxMetrics | None = None,
    ) -> Action | None:
        """Select an unpredictable action from available moves and switches."""
        del movements, type_chart, metrics

        actions = get_available_actions(battle, instances, trainer_id)
        if not actions:
            return None
        return choice(actions)


class MinimaxActionSelector(ActionSelector):
    """Select action using Minimax algorithm with Alpha-Beta pruning.

    This selector evaluates both attacks and switch actions in the same
    decision tree, enabling tactical switches that are not just reactive
    to fainted Pokemon.

    Args:
        ai_level: AI difficulty level (2 = MEDIUM, 3 = HARD MANUAL, 4 = HARD GA).
        depth: Maximum search depth (default 3).
    """

    def __init__(
        self,
        ai_level: AIDifficultyLevel,
        depth: int = DEFAULT_MINIMAX_DEPTH,
        level_3_weights: Mapping[str, float] | None = None,
    ):
        self.ai_level = ai_level
        self.depth = depth
        self.level_3_weights = level_3_weights
        self.last_metrics = MinimaxMetrics()
        if ai_level == AI_LEVEL_MEDIUM:
            self.heuristic_func = evaluate_level_2
        elif ai_level == AI_LEVEL_HARD_MANUAL:
            self.heuristic_func = evaluate_level_3_manual
        elif ai_level == AI_LEVEL_HARD_GA and level_3_weights is None:
            self.heuristic_func = evaluate_level_3_ga
        elif ai_level == AI_LEVEL_HARD_GA:

            def weighted_level_3(battle_state, battle_instances, player_trainer_id, movements=None, type_chart=None, move_effects=None):  # noqa: PLR0913
                return evaluate_level_3_weighted(
                    battle_state,
                    battle_instances,
                    player_trainer_id,
                    movements=movements,
                    type_chart=type_chart,
                    move_effects=move_effects,
                    weights=level_3_weights,
                )

            self.heuristic_func = weighted_level_3
        else:
            raise ValueError(f"Unsupported Minimax AI level: {ai_level}")

    def select(  # noqa: PLR0913
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        trainer_id: str,
        movements: Mapping[str, Movement] | None = None,
        type_chart: Mapping[str, Type] | None = None,
        metrics: MinimaxMetrics | None = None,
    ) -> Action | None:
        """Select the best action using Minimax with Alpha-Beta pruning."""
        opponent_trainer_id = get_opponent_trainer_id(battle, trainer_id)
        if opponent_trainer_id is None:
            return None

        actions = get_available_actions(battle, instances, trainer_id)
        if not actions:
            return None

        best_action = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        search_metrics = metrics if metrics is not None else MinimaxMetrics()
        self.last_metrics = search_metrics

        search_depth = max(0, self.depth - 1)
        for action in actions:
            next_battle, next_instances = simulate_state_transition(
                battle,
                instances,
                action,
                trainer_id,
                opponent_trainer_id,
                movements,
                type_chart,
            )
            score = minimax(
                next_battle,
                next_instances,
                trainer_id,
                search_depth,
                alpha,
                beta,
                False,
                self.heuristic_func,
                movements,
                type_chart,
                metrics=search_metrics,
            )
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, score)

        return best_action
