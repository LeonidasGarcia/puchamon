"""Run the 150 battles-per-row concurrent seeded benchmark."""

from seeded_benchmark_runner import run_configured_benchmark

if __name__ == "__main__":
    run_configured_benchmark(
        battles_per_row=150,
        default_concurrency=4,
        default_output_dir="benchmark-results/150-por-fila-concurrente",
    )
