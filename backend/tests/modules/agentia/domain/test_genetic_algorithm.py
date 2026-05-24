"""Tests for the real-coded genetic algorithm."""

import pytest

from puchamon.modules.agentia.domain.genetic_algorithm import (
    GENETIC_WEIGHT_NAMES,
    FitnessEvaluation,
    GeneticAlgorithmConfig,
    RealCodedGeneticAlgorithm,
    chromosome_to_weight_mapping,
    normalize_chromosome,
    weight_mapping_to_chromosome,
)


def test_normalize_chromosome_clamps_and_sums_to_one():
    chromosome = normalize_chromosome((2.0, -1.0, 1.0, 0.0, 0.0, 0.0, 0.0))

    assert chromosome[0] == pytest.approx(2 / 3)
    assert chromosome[1] == 0.0
    assert chromosome[2] == pytest.approx(1 / 3)
    assert sum(chromosome) == pytest.approx(1.0)


def test_weight_mapping_roundtrip_keeps_named_weights_normalized():
    weights = {"hp": 2.0, "damage": 1.0}

    chromosome = weight_mapping_to_chromosome(weights)
    mapped_weights = chromosome_to_weight_mapping(chromosome)

    assert set(mapped_weights) == set(GENETIC_WEIGHT_NAMES)
    assert mapped_weights["hp"] == pytest.approx(2 / 3)
    assert mapped_weights["damage"] == pytest.approx(1 / 3)
    assert sum(mapped_weights.values()) == pytest.approx(1.0)


def test_genetic_algorithm_keeps_best_elite_individual():
    def evaluator(chromosome):
        return FitnessEvaluation(fitness=chromosome[0], win_rate=chromosome[0])

    config = GeneticAlgorithmConfig(
        population_size=6,
        generations=4,
        elitism_count=1,
        tournament_size=2,
        crossover_rate=1.0,
        mutation_rate=0.0,
        seed=7,
    )
    initial_population = [
        (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    ]

    result = RealCodedGeneticAlgorithm(evaluator, config=config, initial_population=initial_population).run()

    assert result.weights["hp"] == pytest.approx(1.0)
    assert result.best.evaluation.fitness == pytest.approx(1.0)
    assert len(result.history) == config.generations


def test_config_rejects_invalid_population_size():
    with pytest.raises(ValueError, match="population_size"):
        GeneticAlgorithmConfig(population_size=1)


@pytest.mark.asyncio
async def test_genetic_algorithm_supports_async_fitness_evaluator():
    async def evaluator(chromosome):
        return FitnessEvaluation(fitness=chromosome[0], win_rate=chromosome[0])

    config = GeneticAlgorithmConfig(
        population_size=3,
        generations=2,
        elitism_count=1,
        tournament_size=2,
        mutation_rate=0.0,
        seed=11,
    )
    initial_population = [(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)]

    result = await RealCodedGeneticAlgorithm(evaluator, config=config, initial_population=initial_population).run_async()

    assert result.weights["hp"] == pytest.approx(1.0)
