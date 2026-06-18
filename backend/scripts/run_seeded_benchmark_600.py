"""Run the 600 battles-per-row concurrent seeded benchmark."""

from seeded_benchmark_runner import run_configured_benchmark

if __name__ == "__main__":
    run_configured_benchmark(
        battles_per_row=600,
        default_concurrency=6,
        default_output_dir="benchmark-results/600-por-fila-concurrente",
    )
