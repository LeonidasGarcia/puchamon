"""Manual and GA-optimized weights for advanced AI heuristics."""

from typing import Final

LEVEL_3_MANUAL_WEIGHTS: Final[dict[str, float]] = {
    "hp": 0.25,
    "alive": 0.15,
    "damage": 0.25,
    "type": 0.15,
    "speed": 0.08,
    "status": 0.07,
    "effects": 0.05,
}

LEVEL_3_GA_OPTIMIZED_WEIGHTS: Final[dict[str, float]] = {
    "hp": 0.3275128446735863,
    "alive": 0.05326217511460886,
    "damage": 0.11154927979175683,
    "type": 0.01583918477846048,
    "speed": 0.2759869418372587,
    "status": 0.16541348795480293,
    "effects": 0.05043608584952595,
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
