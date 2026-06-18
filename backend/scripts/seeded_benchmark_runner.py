"""Shared runner for seeded AI benchmark scripts."""

import argparse
import asyncio
import os
import sys
from datetime import UTC, datetime
from time import perf_counter

from loguru import logger

from puchamon.modules.agentia.domain.seeded_battle_benchmark import (
    DEFAULT_BATTLE_TYPES,
    DEFAULT_MATCHUPS,
    DEFAULT_MINIMAX_DEPTHS,
    LEVEL_3_GA_OPTIMIZED_WEIGHTS,
    LEVEL_3_MANUAL_WEIGHTS,
    SeededBenchmarkConfig,
    SeededBenchmarkSummary,
    format_seeded_benchmark_table,
    run_seeded_ai_benchmark,
    write_seeded_benchmark_reports,
)
from puchamon.shared.infrastructure.database import init_db

MIN_BATTLES_PER_ROW = 2


def run_configured_benchmark(*, battles_per_row: int, default_concurrency: int, default_output_dir: str) -> None:
    """Run one benchmark size from a small wrapper script."""
    asyncio.run(_run_configured_benchmark(_parse_args(battles_per_row, default_concurrency, default_output_dir)))


def _parse_args(default_battles_per_row: int, default_concurrency: int, default_output_dir: str) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a concurrent seeded AI-vs-AI benchmark.")
    parser.add_argument("--battles-per-row", type=int, default=int(os.getenv("SEEDED_BENCHMARK_BATTLES_PER_ROW", default_battles_per_row)))
    parser.add_argument("--concurrency", type=int, default=int(os.getenv("SEEDED_BENCHMARK_CONCURRENCY", default_concurrency)))
    parser.add_argument("--max-turns", type=int, default=int(os.getenv("SEEDED_BENCHMARK_MAX_TURNS", "80")))
    parser.add_argument("--depths", nargs="+", type=int, choices=DEFAULT_MINIMAX_DEPTHS, default=DEFAULT_MINIMAX_DEPTHS)
    parser.add_argument("--output-dir", default=os.getenv("SEEDED_BENCHMARK_OUTPUT_DIR", default_output_dir))
    parser.add_argument("--prefix", default="real_ai_benchmark")
    parser.add_argument("--log-level", default=os.getenv("SEEDED_BENCHMARK_LOG_LEVEL", "WARNING"))
    return parser.parse_args()


async def _run_configured_benchmark(args: argparse.Namespace) -> None:
    if args.battles_per_row < MIN_BATTLES_PER_ROW or args.battles_per_row % MIN_BATTLES_PER_ROW != 0:
        raise ValueError("--battles-per-row must be an even integer greater than or equal to 2")
    if args.concurrency < 1:
        raise ValueError("--concurrency must be at least 1")
    _configure_logging(args.log_level)

    repetitions_per_side = args.battles_per_row // 2
    expected_rows = len(tuple(args.depths)) * len(DEFAULT_MATCHUPS) * len(DEFAULT_BATTLE_TYPES)
    total_battles = expected_rows * args.battles_per_row
    completed_rows = 0

    def report_progress(summary: SeededBenchmarkSummary) -> None:
        nonlocal completed_rows
        completed_rows += 1
        matchup = summary.to_dict()["matchup"]
        print(
            f"[{completed_rows}/{expected_rows}] depth={summary.minimax_depth} {matchup} {summary.battle_type}: "
            f"{summary.battles} batallas"
        )

    print("Iniciando benchmark seeded concurrente")
    print(f"- batallas por fila: {args.battles_per_row}")
    print(f"- filas esperadas: {expected_rows}")
    print(f"- batallas totales: {total_battles}")
    print(f"- concurrencia: {args.concurrency}")
    print(f"- max turns: {args.max_turns}")
    print(f"- output dir: {args.output_dir}")

    await init_db()
    started_at = datetime.now(UTC)
    start_counter = perf_counter()
    summaries = await run_seeded_ai_benchmark(
        SeededBenchmarkConfig(
            repetitions_per_side=repetitions_per_side,
            max_turns=args.max_turns,
            minimax_depths=tuple(args.depths),
            cleanup_created_battles=True,
            concurrency=args.concurrency,
            progress_callback=report_progress,
        )
    )
    elapsed_seconds = perf_counter() - start_counter
    finished_at = datetime.now(UTC)

    print("\nREAL SEEDED AI BENCHMARK")
    print(format_seeded_benchmark_table(summaries))
    print(f"\nTiempo total benchmark: {elapsed_seconds:.2f} segundos ({elapsed_seconds / 60:.2f} minutos)")

    written_paths = write_seeded_benchmark_reports(
        summaries,
        args.output_dir,
        prefix=args.prefix,
        metadata={
            "level_3_weights_source": "code_default",
            "level_3_weights": LEVEL_3_GA_OPTIMIZED_WEIGHTS,
            "manual_weights": LEVEL_3_MANUAL_WEIGHTS,
            "minimax_depths": tuple(args.depths),
            "battles_per_row": args.battles_per_row,
            "total_battles": sum(summary.battles for summary in summaries),
            "expected_total_battles": total_battles,
            "concurrency": args.concurrency,
            "max_turns": args.max_turns,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "elapsed_seconds": elapsed_seconds,
            "elapsed_minutes": elapsed_seconds / 60,
        },
    )
    print("\nReportes guardados:")
    for report_type, path in written_paths.items():
        print(f"- {report_type}: {path}")


def _configure_logging(log_level: str) -> None:
    logger.remove()
    logger.add(sys.stderr, level=log_level.upper())
