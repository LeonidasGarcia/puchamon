"""Tests for real seeded AI benchmark report utilities."""

import json

from puchamon.modules.agentia.domain.seeded_battle_benchmark import (
    SeededBenchmarkSummary,
    SeededGeneticFitnessConfig,
    format_seeded_benchmark_table,
    save_level_3_weights,
    write_seeded_benchmark_reports,
)
from puchamon.modules.agentia.domain.genetic_algorithm import (
    EvaluatedIndividual,
    FitnessEvaluation,
    GenerationReport,
    GeneticAlgorithmConfig,
    GeneticAlgorithmResult,
    normalize_chromosome,
)


def test_format_seeded_benchmark_table_outputs_real_comparison_rows():
    summaries = [
        SeededBenchmarkSummary(
            level_a=1,
            level_b=4,
            battle_type="1v1",
            minimax_depth=2,
            battles=2,
            wins_level_a=0,
            wins_level_b=2,
            draws=0,
            average_turns=8.5,
            average_winner_hp=0.42,
            average_decision_time_ms=1.25,
            average_nodes_visited=32.0,
            average_pruned_branches=6.0,
        )
    ]

    table = format_seeded_benchmark_table(summaries)

    assert "Facil vs Dificil GA" in table
    assert "| Depth | Matchup | Formato | Batallas |" in table
    assert "Dificil GA" in table
    assert "32.00" in table


def test_write_seeded_benchmark_reports_writes_markdown_json_and_csv(tmp_path):
    summaries = [
        SeededBenchmarkSummary(
            level_a=2,
            level_b=4,
            battle_type="3v3",
            minimax_depth=4,
            battles=4,
            wins_level_a=1,
            wins_level_b=3,
            draws=0,
            average_turns=14.0,
            average_winner_hp=0.33,
            average_decision_time_ms=2.5,
            average_nodes_visited=54.0,
            average_pruned_branches=12.0,
        )
    ]

    paths = write_seeded_benchmark_reports(
        summaries,
        tmp_path,
        prefix="sample",
        metadata={"level_3_weights_source": "trained_this_run", "level_3_weights": {"hp": 0.5, "damage": 0.5}},
    )

    assert paths["markdown"].read_text(encoding="utf-8").startswith("# Real AI Benchmark")
    assert paths["csv"].read_text(encoding="utf-8").startswith("matchup,")
    data = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert data["metadata"]["level_3_weights_source"] == "trained_this_run"
    assert data["summaries"][0]["matchup"] == "Intermedio vs Dificil GA"
    assert data["summaries"][0]["battle_type"] == "3v3"
    assert data["summaries"][0]["minimax_depth"] == 4
    assert data["summaries"][0]["average_nodes_visited"] == 54.0


def test_seeded_genetic_fitness_config_accepts_all_battle_types():
    config = SeededGeneticFitnessConfig(battle_types=("1v1", "2v2", "3v3"), matches_per_opponent=10)

    assert config.battle_types == ("1v1", "2v2", "3v3")
    assert config.matches_per_opponent == 10


def test_save_level_3_weights_writes_production_weight_module(tmp_path):
    chromosome = normalize_chromosome((0.2, 0.1, 0.1, 0.15, 0.2, 0.05, 0.2))
    individual = EvaluatedIndividual(
        chromosome=chromosome,
        evaluation=FitnessEvaluation(fitness=0.7, win_rate=0.6, hp_remaining_score=0.5, average_turns=8.0),
    )
    result = GeneticAlgorithmResult(
        best=individual,
        history=[GenerationReport(generation=1, best=individual, average_fitness=0.7)],
        config=GeneticAlgorithmConfig(population_size=2, generations=1, elitism_count=1, tournament_size=2),
    )
    target_path = tmp_path / "genetic_weights.py"

    saved_path = save_level_3_weights(result.weights, result, target_path=target_path)

    content = saved_path.read_text(encoding="utf-8")
    assert "LEVEL_3_MANUAL_WEIGHTS" in content
    assert '"hp": 0.2' in content
    assert '"source": "saved_from_ai_real_benchmark"' in content
    assert '"fitness_value": 0.7' in content
