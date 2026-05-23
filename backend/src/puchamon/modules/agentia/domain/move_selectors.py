"""Move selection strategies for AI."""

import copy
import random
from abc import ABC, abstractmethod
from collections.abc import Callable

from ...battle.domain.entities import Battle, BattleInstance, MoveState
from ...pokedex.domain.entities import Movement
from .heuristics import calculate_hp_score, evaluate_level_2, get_opponent_hp_values

Action = tuple[str, str]


class MoveSelector(ABC):
    """Abstract base class for move selection strategies."""

    @abstractmethod
    def select(self, available_moves: list[MoveState]) -> str | None:
        """Select a move from available moves.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            The move_id selected or None if no move available.
        """
        pass


class RandomMoveSelector(MoveSelector):
    """Select a move randomly (Level 1 - Easy)."""

    def select(self, available_moves: list[MoveState]) -> str | None:
        """Select a random move.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            A random move_id or None if no moves available.
        """
        return random.choice(available_moves).move_id if available_moves else None


class GreedyHPMoveSelector(MoveSelector):
    """Select move using greedy best-first with HP-based heuristic.

    Heuristic: h(move) = 1 - HP_oponente_post_percent
    Objective: Minimize opponent HP after attack (maximize damage).
    """

    def __init__(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        movements: dict | None = None,
    ):
        self.battle = battle
        self.instances = instances
        self.movements = movements

    def select(self, available_moves: list[MoveState]) -> str | None:
        """Select move with highest damage potential.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            The move_id with best h-score or None if no moves available.
        """
        if not available_moves:
            return None

        if not self.battle or not self.instances:
            return available_moves[0].move_id

        opponent_hp = get_opponent_hp_values(self.battle, self.instances)
        if not opponent_hp:
            return available_moves[0].move_id

        opponent_current, opponent_max = opponent_hp

        def get_h_score(ms: MoveState) -> float:
            move = self.movements.get(ms.move_id) if self.movements else None
            if not move or not move.power:
                return 0.0
            return calculate_hp_score(move.power, opponent_current, opponent_max)

        best_move_state = max(available_moves, key=get_h_score)
        return best_move_state.move_id


class MinimaxMoveSelector(MoveSelector):
    """Select move using Minimax algorithm with Alpha-Beta pruning.

    This selector evaluates both attacks and switch actions in the same
    decision tree, enabling tactical switches that are not just reactive
    to fainted Pokemon.

    Args:
        battle: The current battle state.
        instances: Dict of battle instances keyed by ID.
        player_trainer_id: The trainer ID of the AI player.
        movements: Dict of Movement entities keyed by ID.
        depth: Maximum search depth (default 3).
        heuristic_func: Heuristic function to evaluate leaf nodes.
    """

    def __init__(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        player_trainer_id: str,
        movements: dict | None = None,
        depth: int = 3,
        heuristic_func: Callable[[Battle, dict[str, BattleInstance], str], float] | None = None,
    ):
        self.battle = battle
        self.instances = instances
        self.player_trainer_id = player_trainer_id
        self.movements = movements
        self.depth = depth
        self.heuristic_func = heuristic_func or evaluate_level_2

    def select(self, available_moves: list[MoveState]) -> str | None:
        """Select the best action using Minimax with Alpha-Beta pruning.

        Args:
            available_moves: List of MoveState with PP > 0.

        Returns:
            The move_id selected or None if no moves available.
        """
        if not available_moves:
            return None

        opponent_trainer_id = self._get_opponent_trainer_id()
        if opponent_trainer_id is None:
            return available_moves[0].move_id

        actions = self._get_available_actions(self.battle, self.instances)

        if not actions:
            return available_moves[0].move_id

        best_action = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for action in actions:
            state_copy = self._simulate_action(
                copy.deepcopy(self.battle),
                copy.deepcopy(self.instances),
                action,
                self.player_trainer_id,
                opponent_trainer_id,
            )
            score = self._minimax(
                state_copy[0],
                self.depth - 1,
                alpha,
                beta,
                False,
                opponent_trainer_id,
            )
            if score > best_score:
                best_score = score
                best_action = action
            alpha = max(alpha, score)

        if best_action is None:
            return available_moves[0].move_id

        if best_action[0] == "MOVE":
            return best_action[1]
        return None

    def _get_available_actions(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
    ) -> list[Action]:
        """Get all available actions (moves and switches) for the player.

        Args:
            battle: The battle state to evaluate.
            instances: The battle instances to evaluate.

        Returns:
            List of Action tuples (action_type, action_id).
        """
        actions: list[Action] = []

        player_side = battle.sides.get(self.player_trainer_id)
        if not player_side:
            return actions

        active_ids = [uid for uid in player_side.active_pokemon_instance_ids if uid is not None]
        active_instance_id = active_ids[0] if active_ids else None

        if active_instance_id:
            active_instance = instances.get(active_instance_id)
            if active_instance and not active_instance.fainted:
                for ms in active_instance.move_state:
                    if ms.current_pp > 0:
                        actions.append(("MOVE", ms.move_id))

        for instance in instances.values():
            if instance.trainer_id != self.player_trainer_id:
                continue
            if instance.fainted:
                continue
            if active_instance_id and instance.id == active_instance_id:
                continue
            if instance.slot is not None:
                continue
            actions.append(("SWITCH", str(instance.id)))

        return actions

    def _simulate_action(
        self,
        battle: Battle,
        instances: dict[str, BattleInstance],
        action: Action,
        player_trainer_id: str,
        opponent_trainer_id: str,
    ) -> tuple[Battle, dict[str, BattleInstance]]:
        """Simulate an action and return the resulting state.

        Args:
            battle: The battle state to modify.
            instances: The battle instances to modify.
            action: The action to simulate (action_type, action_id).
            player_trainer_id: The AI player's trainer ID.
            opponent_trainer_id: The opponent's trainer ID.

        Returns:
            Tuple of (modified_battle, modified_instances).
        """
        action_type, action_id = action

        if action_type == "MOVE":
            move = self.movements.get(action_id) if self.movements else None
            if move is None or move.power is None:
                return battle, instances

            player_side = battle.sides.get(player_trainer_id)
            opponent_side = battle.sides.get(opponent_trainer_id)

            if not player_side or not opponent_side:
                return battle, instances

            player_active_ids = [uid for uid in player_side.active_pokemon_instance_ids if uid is not None]
            opponent_active_ids = [uid for uid in opponent_side.active_pokemon_instance_ids if uid is not None]

            if not player_active_ids or not opponent_active_ids:
                return battle, instances

            player_instance = instances.get(player_active_ids[0])
            opponent_instance = instances.get(opponent_active_ids[0])

            if not player_instance or not opponent_instance:
                return battle, instances

            if player_instance.stats is None or opponent_instance.stats is None:
                return battle, instances

            damage = self._calculate_damage(move, player_instance, opponent_instance)
            opponent_instance.current_hp = max(0, opponent_instance.current_hp - damage)

            if opponent_instance.current_hp <= 0:
                opponent_instance.fainted = True
                opponent_side.active_pokemon_instance_ids[0] = None

        elif action_type == "SWITCH":
            player_side = battle.sides.get(player_trainer_id)
            if not player_side:
                return battle, instances

            current_active_ids = [uid for uid in player_side.active_pokemon_instance_ids if uid is not None]
            new_instance = instances.get(action_id)

            if not new_instance or new_instance.fainted:
                return battle, instances

            if current_active_ids:
                player_side.active_pokemon_instance_ids[0] = action_id
            else:
                player_side.active_pokemon_instance_ids = [action_id]

        return battle, instances

    def _calculate_damage(
        self,
        move: Movement,
        source: BattleInstance,
        target: BattleInstance,
    ) -> int:
        """Calculate damage for a move against a target.

        Args:
            move: The movement being used.
            source: The source battle instance.
            target: The target battle instance.

        Returns:
            Estimated damage value.
        """
        attack_stat_key = "atk" if move.category.lower() == "physical" else "spa"
        defense_stat_key = "def" if move.category.lower() == "physical" else "spd"

        attack = source.stats.atk if attack_stat_key == "atk" else source.stats.spa
        defense = target.stats.def_ if defense_stat_key == "def" else target.stats.spd

        level_factor = (2 * source.level) // 5 + 2
        base_damage = (level_factor * (move.power or 0) * attack) // defense // 50 + 2

        stab = 1.5 if move.type in source.types else 1.0

        effectiveness = 1.0
        base_damage = max(1, base_damage)
        return int(base_damage * stab * effectiveness * 0.85)

    def _minimax(
        self,
        battle: Battle,
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
        _current_player_id: str,
    ) -> float:
        """Minimax algorithm with Alpha-Beta pruning.

        Args:
            battle: The current battle state.
            depth: Remaining search depth.
            alpha: Alpha value for pruning.
            beta: Beta value for pruning.
            maximizing: True if maximizing player's turn.
            current_player_id: The trainer ID whose turn it is.

        Returns:
            The evaluated score for this branch.
        """
        if depth == 0:
            return self.heuristic_func(battle, self.instances, self.player_trainer_id)

        opponent_trainer_id = self._get_opponent_trainer_id()
        if opponent_trainer_id is None:
            return self.heuristic_func(battle, self.instances, self.player_trainer_id)

        actions = self._get_available_actions(self.battle, self.instances)

        if not actions:
            return self.heuristic_func(battle, self.instances, self.player_trainer_id)

        if maximizing:
            max_eval = float("-inf")
            for action in actions:
                state_copy = self._simulate_action(
                    copy.deepcopy(battle),
                    copy.deepcopy(self.instances),
                    action,
                    self.player_trainer_id,
                    opponent_trainer_id,
                )
                eval_score = self._minimax(
                    state_copy[0],
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    opponent_trainer_id,
                )
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            for action in actions:
                state_copy = self._simulate_action(
                    copy.deepcopy(battle),
                    copy.deepcopy(self.instances),
                    action,
                    self.player_trainer_id,
                    opponent_trainer_id,
                )
                eval_score = self._minimax(
                    state_copy[0],
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    self.player_trainer_id,
                )
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _get_opponent_trainer_id(self) -> str | None:
        """Get the opponent's trainer ID.

        Returns:
            The opponent's trainer ID or None if not found.
        """
        for trainer_id in self.battle.sides.keys():
            if trainer_id != self.player_trainer_id:
                return trainer_id
        return None
