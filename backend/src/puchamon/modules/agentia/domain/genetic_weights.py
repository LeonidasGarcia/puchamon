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
    "hp": 0.17069593862952015,
    "alive": 0.11919750829060917,
    "damage": 0.13812122618470588,
    "type": 0.12333016456270111,
    "speed": 0.10660360049220932,
    "status": 0.1315293788060151,
    "effects": 0.21052218303423925,
}

LEVEL_3_GA_TRAINING_METADATA: Final[dict[str, object]] = {
    "algorithm": "real-coded genetic algorithm",
    "selection": "tournament",
    "crossover": "arithmetic",
    "mutation": "gaussian",
    "elitism": True,
    "fitness": "win_rate + 0.1 * hp_remaining_score - 0.05 * normalized_turns",
    "source": "saved_from_ai_real_benchmark",
    "fitness_value": 0.779189092086313,
    "win_rate": 0.7222222222222222,
    "hp_remaining_score": 0.5985575875297974,
    "average_turns": 5.777777777777778,
}
