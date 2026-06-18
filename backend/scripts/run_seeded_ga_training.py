"""Run configurable seeded GA training for hard-GA heuristic weights."""

import argparse
import asyncio
import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from loguru import logger

from puchamon.modules.agentia.domain.genetic_algorithm import GENETIC_WEIGHT_NAMES, GeneticAlgorithmConfig
from puchamon.modules.agentia.domain.genetic_weights import LEVEL_3_GA_OPTIMIZED_WEIGHTS
from puchamon.modules.agentia.domain.seeded_battle_benchmark import (
    AI_LEVEL_EASY,
    AI_LEVEL_HARD_MANUAL,
    AI_LEVEL_MEDIUM,
    DEFAULT_BATTLE_TYPES,
    DEFAULT_MINIMAX_DEPTHS,
    SeededGeneticFitnessConfig,
    format_seeded_ga_history_table,
    run_seeded_genetic_weight_optimization,
    save_level_3_weights,
)
from puchamon.shared.infrastructure.database import init_db


def main() -> None:
    """CLI entrypoint for seeded GA training."""
    asyncio.run(_run(_parse_args()))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train hard-GA weights with real seeded Pokemon battles.")
    parser.add_argument("--population-size", type=int, default=16)
    parser.add_argument("--generations", type=int, default=14)
    parser.add_argument("--elitism-count", type=int, default=1)
    parser.add_argument("--tournament-size", type=int, default=3)
    parser.add_argument("--crossover-rate", type=float, default=0.8)
    parser.add_argument("--mutation-rate", type=float, default=0.15)
    parser.add_argument("--mutation-std", type=float, default=0.05)
    parser.add_argument("--matches-per-opponent", type=int, default=5)
    parser.add_argument("--max-turns", type=int, default=100)
    parser.add_argument("--minimax-depth", type=int, choices=DEFAULT_MINIMAX_DEPTHS, default=2)
    parser.add_argument("--battle-types", nargs="+", choices=DEFAULT_BATTLE_TYPES, default=DEFAULT_BATTLE_TYPES)
    parser.add_argument(
        "--opponents",
        nargs="+",
        type=int,
        choices=(AI_LEVEL_EASY, AI_LEVEL_MEDIUM, AI_LEVEL_HARD_MANUAL),
        default=(AI_LEVEL_EASY, AI_LEVEL_MEDIUM, AI_LEVEL_HARD_MANUAL),
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="benchmark-results/ga-training-30-pokemon-strong")
    parser.add_argument("--save-trained-weights", action="store_true")
    parser.add_argument("--log-level", default="WARNING")
    parser.add_argument("--initial-hp", type=float)
    parser.add_argument("--initial-alive", type=float)
    parser.add_argument("--initial-damage", type=float)
    parser.add_argument("--initial-type", type=float)
    parser.add_argument("--initial-speed", type=float)
    parser.add_argument("--initial-status", type=float)
    parser.add_argument("--initial-effects", type=float)
    return parser.parse_args()


async def _run(args: argparse.Namespace) -> None:
    _configure_logging(args.log_level)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    initial_weights = _resolve_initial_weights(args)
    ga_config = GeneticAlgorithmConfig(
        population_size=args.population_size,
        generations=args.generations,
        elitism_count=args.elitism_count,
        tournament_size=args.tournament_size,
        crossover_rate=args.crossover_rate,
        mutation_rate=args.mutation_rate,
        mutation_std=args.mutation_std,
        matches_per_individual=args.matches_per_opponent,
        seed=args.seed,
    )
    fitness_config = SeededGeneticFitnessConfig(
        opponents=tuple(args.opponents),
        battle_types=tuple(args.battle_types),
        matches_per_opponent=args.matches_per_opponent,
        max_turns=args.max_turns,
        minimax_depth=args.minimax_depth,
        cleanup_created_battles=True,
    )

    print("Iniciando entrenamiento GA seeded")
    print(f"- population size: {args.population_size}")
    print(f"- generations: {args.generations}")
    print(f"- matches per opponent: {args.matches_per_opponent}")
    print(f"- battle types: {', '.join(args.battle_types)}")
    print(f"- opponents: {', '.join(str(opponent) for opponent in args.opponents)}")
    print(f"- minimax depth: {args.minimax_depth}")
    print(f"- max turns: {args.max_turns}")
    print(f"- output dir: {output_dir}")

    await init_db()
    started_at = datetime.now(UTC)
    start_counter = perf_counter()
    result = await run_seeded_genetic_weight_optimization(ga_config=ga_config, fitness_config=fitness_config, initial_weights=initial_weights)
    elapsed_seconds = perf_counter() - start_counter
    finished_at = datetime.now(UTC)

    print("\nREAL SEEDED GA TRAINING")
    print(format_seeded_ga_history_table(result))
    print("\nPesos entrenados:")
    print(json.dumps(result.weights, indent=2, ensure_ascii=False))
    print(f"\nTiempo total entrenamiento: {elapsed_seconds:.2f} segundos ({elapsed_seconds / 60:.2f} minutos)")

    payload = {
        "metadata": {
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "elapsed_seconds": elapsed_seconds,
            "elapsed_minutes": elapsed_seconds / 60,
            "initial_weights": initial_weights,
            "ga_config": asdict(ga_config),
            "fitness_config": asdict(fitness_config),
        },
        "result": result.to_dict(),
    }
    json_path = output_dir / "level3_ga_training.json"
    markdown_path = output_dir / "level3_ga_training.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(_format_training_markdown(payload), encoding="utf-8")

    print("\nReportes guardados:")
    print(f"- json: {json_path}")
    print(f"- markdown: {markdown_path}")

    if args.save_trained_weights:
        saved_path = save_level_3_weights(result.weights, result)
        print(f"\nPesos GA persistidos en: {saved_path}")


def _resolve_initial_weights(args: argparse.Namespace) -> dict[str, float]:
    weights = dict(LEVEL_3_GA_OPTIMIZED_WEIGHTS)
    for name in GENETIC_WEIGHT_NAMES:
        value = getattr(args, f"initial_{name}")
        if value is not None:
            weights[name] = value
    return weights


def _format_training_markdown(payload: dict) -> str:
    metadata = payload["metadata"]
    result = payload["result"]
    weights = result["weights"]
    lines = [
        "# Real Seeded GA Training",
        "",
        f"- started_at: {metadata['started_at']}",
        f"- finished_at: {metadata['finished_at']}",
        f"- elapsed_seconds: {metadata['elapsed_seconds']:.2f}",
        f"- elapsed_minutes: {metadata['elapsed_minutes']:.2f}",
        f"- fitness: {result['fitness']:.6f}",
        f"- win_rate: {result['win_rate']:.2%}",
        f"- hp_remaining_score: {result['hp_remaining_score']:.2%}",
        f"- average_turns: {result['average_turns']:.2f}",
        "",
        "## Pesos Entrenados",
        "",
    ]
    lines.extend(f"- {name}: {weights[name]:.6f}" for name in GENETIC_WEIGHT_NAMES)
    lines.extend(["", "## Historial", "", "| Generacion | Mejor Fitness | Fitness Promedio |", "| ---: | ---: | ---: |"])
    for entry in result["history"]:
        lines.append(f"| {entry['generation']} | {entry['best']['fitness']:.6f} | {entry['average_fitness']:.6f} |")
    return "\n".join(lines) + "\n"


def _configure_logging(log_level: str) -> None:
    logger.remove()
    logger.add(sys.stderr, level=log_level.upper())


if __name__ == "__main__":
    main()
