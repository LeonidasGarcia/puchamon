"""GA-optimized heuristic weights for the production Level 3 AI."""

from typing import Final

LEVEL_3_GA_OPTIMIZED_WEIGHTS: Final[dict[str, float]] = {
    "hp": 0.1765587813083075,
    "alive": 0.10915206417431861,
    "damage": 0.06431245818093839,
    "type": 0.13295716536225582,
    "speed": 0.21534318608690411,
    "status": 0.07519547353909556,
    "effects": 0.22648087134818007,
}

LEVEL_3_GA_TRAINING_METADATA: Final[dict[str, object]] = {
    "algorithm": "real-coded genetic algorithm",
    "selection": "tournament",
    "crossover": "arithmetic",
    "mutation": "gaussian",
    "elitism": True,
    "fitness": "win_rate + 0.1 * hp_remaining_score - 0.05 * normalized_turns",
    "source": "benchmark-results/level3_ga_training.json",
    "fitness_value": 0.6731253035593929,
    "win_rate": 0.6222222222222222,
    "hp_remaining_score": 0.5484752578161507,
    "average_turns": 6.311111111111111,
}
