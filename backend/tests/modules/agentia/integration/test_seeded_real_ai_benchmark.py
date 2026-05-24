"""Optional real seeded AI benchmark.

This test is skipped by default because it requires MongoDB, Beanie initialization and the real seed data from
``frontend/pokemon.js``. It is meant to be run manually when you want production-like AI-vs-AI numbers.

How to run from ``backend/``:
    RUN_REAL_AI_BENCHMARK=1 uv run pytest tests/modules/agentia/integration/test_seeded_real_ai_benchmark.py -s

Useful knobs:
    REAL_AI_BENCHMARK_REPETITIONS=1   # total battles = 3 matchups * 3 formats * repetitions * 2
    REAL_AI_BENCHMARK_MAX_TURNS=80    # battles that exceed this limit are counted as no-winner runs

Before running, make sure your database is configured in ``.env`` and the frontend seed was loaded into MongoDB.
"""

import os

import pytest

from puchamon.modules.agentia.domain.seeded_battle_benchmark import (
    SeededBenchmarkConfig,
    format_seeded_benchmark_table,
    run_seeded_ai_benchmark,
    write_seeded_benchmark_reports,
)
from puchamon.shared.infrastructure.database import init_db


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_REAL_AI_BENCHMARK") != "1",
    reason="Set RUN_REAL_AI_BENCHMARK=1 to run the MongoDB-backed seeded AI benchmark manually.",
)


@pytest.mark.asyncio
async def test_seeded_real_ai_benchmark_outputs_table():
    """Run a real benchmark using seeded Pokemon, moves, effects and the actual battle engine."""
    # Edit these env vars instead of changing the test when you want more battles.
    repetitions_per_side = int(os.getenv("REAL_AI_BENCHMARK_REPETITIONS", "1"))
    max_turns = int(os.getenv("REAL_AI_BENCHMARK_MAX_TURNS", "80"))
    output_dir = os.getenv("REAL_AI_BENCHMARK_OUTPUT_DIR")

    await init_db()
    summaries = await run_seeded_ai_benchmark(
        SeededBenchmarkConfig(
            repetitions_per_side=repetitions_per_side,
            max_turns=max_turns,
            cleanup_created_battles=True,
        )
    )

    table = format_seeded_benchmark_table(summaries)
    print("\nREAL SEEDED AI BENCHMARK")
    print(table)
    if output_dir:
        written_paths = write_seeded_benchmark_reports(summaries, output_dir, metadata={"level_3_weights_source": "code_default"})
        print("\nReportes guardados:")
        for report_type, path in written_paths.items():
            print(f"- {report_type}: {path}")

    assert len(summaries) == 9
    assert sum(summary.battles for summary in summaries) == 18 * repetitions_per_side
