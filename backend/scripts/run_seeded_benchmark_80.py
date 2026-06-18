"""Run the 80 battles-per-row concurrent seeded benchmark."""

from seeded_benchmark_runner import run_configured_benchmark

if __name__ == "__main__":
    run_configured_benchmark(
        battles_per_row=80,
        default_concurrency=4,
        default_output_dir="benchmark-results/80-por-fila-concurrente",
    )
