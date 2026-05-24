"""Real AI-vs-AI benchmark using the seeded Pokedex data and battle engine.

It uses Beanie/MongoDB, the seeded data from ``frontend/pokemon.js`` and the real battle services. This is the only
benchmark path kept for AI reports because it exercises the same flow used by frontend/backend battles.
"""

import argparse
import asyncio
import csv
import json
import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from ....shared.infrastructure.database import init_db
from ...battle.application.services.battle_service import BattleService
from ...battle.application.services.battle_setup_service import BattleSetupService
from ...battle.domain.entities import Battle, BattleInstance, Player, TurnAction
from ..application.services.ia_service import IAService
from .action_selectors import AI_LEVEL_EASY, AI_LEVEL_HARD, AI_LEVEL_MEDIUM
from .genetic_algorithm import (
    GENETIC_WEIGHT_NAMES,
    Chromosome,
    FitnessEvaluation,
    GeneticAlgorithmConfig,
    GeneticAlgorithmResult,
    RealCodedGeneticAlgorithm,
    chromosome_to_weight_mapping,
    weight_mapping_to_chromosome,
)
from .genetic_weights import LEVEL_3_GA_OPTIMIZED_WEIGHTS, LEVEL_3_GA_TRAINING_METADATA

BattleType = Literal["1v1", "2v2", "3v3"]
AILevel = Literal[1, 2, 3]

AI_LEVEL_LABELS: dict[int, str] = {
    AI_LEVEL_EASY: "Facil",
    AI_LEVEL_MEDIUM: "Intermedio",
    AI_LEVEL_HARD: "Dificil GA",
}
DEFAULT_MATCHUPS: tuple[tuple[AILevel, AILevel], ...] = (
    (AI_LEVEL_EASY, AI_LEVEL_MEDIUM),
    (AI_LEVEL_EASY, AI_LEVEL_HARD),
    (AI_LEVEL_MEDIUM, AI_LEVEL_HARD),
)
DEFAULT_BATTLE_TYPES: tuple[BattleType, ...] = ("1v1", "2v2", "3v3")


@dataclass(frozen=True, slots=True)
class SeededBenchmarkConfig:
    """Configuration for the real seeded AI benchmark.

    Change ``repetitions_per_side`` to control total battle count:
    total = len(matchups) * len(battle_types) * repetitions_per_side * 2.

    Examples:
    - 1 repetition  -> 18 battles with the default matrix.
    - 34 repetitions -> 612 battles with the default matrix.

    ``max_turns`` avoids a runaway battle. A battle that reaches this limit is counted as a draw.
    """

    matchups: tuple[tuple[AILevel, AILevel], ...] = DEFAULT_MATCHUPS
    battle_types: tuple[BattleType, ...] = DEFAULT_BATTLE_TYPES
    repetitions_per_side: int = 1
    max_turns: int = 120
    cleanup_created_battles: bool = True
    level_3_weights: Mapping[str, float] | None = None


@dataclass(frozen=True, slots=True)
class SeededGeneticFitnessConfig:
    """Configuration for training GA weights through real seeded battles."""

    opponents: tuple[AILevel, ...] = (AI_LEVEL_EASY, AI_LEVEL_MEDIUM, AI_LEVEL_HARD)
    battle_types: tuple[BattleType, ...] = ("1v1",)
    matches_per_opponent: int = 1
    max_turns: int = 80
    cleanup_created_battles: bool = True


@dataclass(frozen=True, slots=True)
class SeededBattleResult:
    """Result of one real seeded AI-vs-AI battle."""

    level_a: AILevel
    level_b: AILevel
    battle_type: BattleType
    turns: int
    winner_level: AILevel | None
    winner_trainer_id: str | None
    remaining_hp_score: float
    reason: str


@dataclass(frozen=True, slots=True)
class SeededBenchmarkSummary:
    """Aggregated real benchmark metrics for one matchup and battle type."""

    level_a: AILevel
    level_b: AILevel
    battle_type: BattleType
    battles: int
    wins_level_a: int
    wins_level_b: int
    draws: int
    average_turns: float
    average_winner_hp: float

    @property
    def best_ai(self) -> str:
        """Return the winner label for this row."""
        if self.wins_level_a == self.wins_level_b:
            return "Empate"
        return AI_LEVEL_LABELS[self.level_a] if self.wins_level_a > self.wins_level_b else AI_LEVEL_LABELS[self.level_b]

    def to_row(self) -> list[str]:
        """Return this summary as a markdown row."""
        winrate_a = self.wins_level_a / self.battles if self.battles else 0.0
        winrate_b = self.wins_level_b / self.battles if self.battles else 0.0
        return [
            f"{AI_LEVEL_LABELS[self.level_a]} vs {AI_LEVEL_LABELS[self.level_b]}",
            self.battle_type,
            str(self.battles),
            str(self.wins_level_a),
            str(self.wins_level_b),
            str(self.draws),
            f"{winrate_a:.2%}",
            f"{winrate_b:.2%}",
            f"{self.average_turns:.2f}",
            f"{self.average_winner_hp:.2%}",
            self.best_ai,
        ]

    def to_dict(self) -> dict[str, Any]:
        """Return this summary as a serializable dictionary."""
        return {
            "matchup": f"{AI_LEVEL_LABELS[self.level_a]} vs {AI_LEVEL_LABELS[self.level_b]}",
            "level_a": self.level_a,
            "level_b": self.level_b,
            "battle_type": self.battle_type,
            "battles": self.battles,
            "wins_level_a": self.wins_level_a,
            "wins_level_b": self.wins_level_b,
            "draws": self.draws,
            "winrate_a": self.wins_level_a / self.battles if self.battles else 0.0,
            "winrate_b": self.wins_level_b / self.battles if self.battles else 0.0,
            "average_turns": self.average_turns,
            "average_winner_hp": self.average_winner_hp,
            "best_ai": self.best_ai,
        }


async def run_seeded_ai_benchmark(config: SeededBenchmarkConfig | None = None) -> list[SeededBenchmarkSummary]:
    """Run the real AI-vs-AI benchmark against seeded MongoDB data.

    The database must already be initialized and seeded. In practice, run this from the integration test or from an
    application context after calling ``init_db``.
    """
    resolved_config = config or SeededBenchmarkConfig()
    battle_service = BattleService()
    ia_service = IAService()
    summaries: list[SeededBenchmarkSummary] = []

    await _assert_seeded_data_available(battle_service)

    for level_a, level_b in resolved_config.matchups:
        for battle_type in resolved_config.battle_types:
            results: list[SeededBattleResult] = []
            for _ in range(resolved_config.repetitions_per_side):
                results.append(
                    await _run_single_seeded_battle(
                        battle_service=battle_service,
                        ia_service=ia_service,
                        level_a=level_a,
                        level_b=level_b,
                        battle_type=battle_type,
                        config=resolved_config,
                        level_a_weights=resolved_config.level_3_weights if level_a == AI_LEVEL_HARD else None,
                        level_b_weights=resolved_config.level_3_weights if level_b == AI_LEVEL_HARD else None,
                    )
                )
                results.append(
                    await _run_single_seeded_battle(
                        battle_service=battle_service,
                        ia_service=ia_service,
                        level_a=level_b,
                        level_b=level_a,
                        battle_type=battle_type,
                        config=resolved_config,
                        level_a_weights=resolved_config.level_3_weights if level_b == AI_LEVEL_HARD else None,
                        level_b_weights=resolved_config.level_3_weights if level_a == AI_LEVEL_HARD else None,
                    )
                )
            summaries.append(_summarize_results(level_a, level_b, battle_type, results))
    return summaries


def format_seeded_benchmark_table(summaries: list[SeededBenchmarkSummary]) -> str:
    """Format real seeded benchmark summaries as a markdown table."""
    headers = [
        "Matchup",
        "Formato",
        "Batallas",
        "Wins A",
        "Wins B",
        "Empates",
        "Winrate A",
        "Winrate B",
        "Turnos Prom.",
        "HP Restante",
        "Mejor IA",
    ]
    separator = ["---", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---:", "---"]
    rows = [headers, separator]
    rows.extend(summary.to_row() for summary in summaries)
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def format_seeded_ga_history_table(result: GeneticAlgorithmResult) -> str:
    """Format a real-battle GA training result as a markdown table."""
    headers = ["Generacion", "Mejor Fitness", "Winrate", "HP Restante", "Turnos Prom.", "Pesos"]
    separator = ["---:", "---:", "---:", "---:", "---:", "---"]
    rows = [headers, separator]
    for report in result.history:
        evaluation = report.best.evaluation
        weights = chromosome_to_weight_mapping(report.best.chromosome)
        weight_text = ", ".join(f"{key}={value:.2f}" for key, value in weights.items())
        rows.append(
            [
                str(report.generation),
                f"{evaluation.fitness:.4f}",
                f"{evaluation.win_rate:.2%}",
                f"{evaluation.hp_remaining_score:.2%}",
                f"{evaluation.average_turns:.2f}",
                weight_text,
            ]
        )
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def write_seeded_benchmark_reports(
    summaries: list[SeededBenchmarkSummary],
    output_dir: str | Path,
    prefix: str = "real_ai_benchmark",
    metadata: Mapping[str, Any] | None = None,
) -> dict[str, Path]:
    """Write benchmark summaries as Markdown, JSON and CSV files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    rows = [summary.to_dict() for summary in summaries]
    report_payload = {"metadata": dict(metadata or {}), "summaries": rows}
    markdown_path = output_path / f"{prefix}.md"
    json_path = output_path / f"{prefix}.json"
    csv_path = output_path / f"{prefix}.csv"

    metadata_text = _format_report_metadata(metadata or {})
    markdown_path.write_text(metadata_text + format_seeded_benchmark_table(summaries) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=list(rows[0].keys()) if rows else [])
        writer.writeheader()
        writer.writerows(rows)

    return {"markdown": markdown_path, "json": json_path, "csv": csv_path}


def save_level_3_weights(
    weights: Mapping[str, float],
    training_result: GeneticAlgorithmResult,
    target_path: str | Path | None = None,
) -> Path:
    """Persist trained GA weights as the production Level 3 defaults."""
    destination = Path(target_path) if target_path is not None else Path(__file__).with_name("genetic_weights.py")
    ordered_weights = {name: float(weights[name]) for name in GENETIC_WEIGHT_NAMES}
    evaluation = training_result.best.evaluation
    content = _format_genetic_weights_module(ordered_weights, evaluation)
    destination.write_text(content, encoding="utf-8")
    return destination


def _format_genetic_weights_module(weights: Mapping[str, float], evaluation: FitnessEvaluation) -> str:
    weight_lines = [f'    "{name}": {weights[name]!r},' for name in GENETIC_WEIGHT_NAMES]
    return (
        '"""GA-optimized heuristic weights for the production Level 3 AI."""\n\n'
        "from typing import Final\n\n"
        "LEVEL_3_GA_OPTIMIZED_WEIGHTS: Final[dict[str, float]] = {\n"
        + "\n".join(weight_lines)
        + "\n}\n\n"
        "LEVEL_3_GA_TRAINING_METADATA: Final[dict[str, object]] = {\n"
        '    "algorithm": "real-coded genetic algorithm",\n'
        '    "selection": "tournament",\n'
        '    "crossover": "arithmetic",\n'
        '    "mutation": "gaussian",\n'
        '    "elitism": True,\n'
        '    "fitness": "win_rate + 0.1 * hp_remaining_score - 0.05 * normalized_turns",\n'
        '    "source": "saved_from_ai_real_benchmark",\n'
        f'    "fitness_value": {evaluation.fitness!r},\n'
        f'    "win_rate": {evaluation.win_rate!r},\n'
        f'    "hp_remaining_score": {evaluation.hp_remaining_score!r},\n'
        f'    "average_turns": {evaluation.average_turns!r},\n'
        "}\n"
    )


def _format_report_metadata(metadata: Mapping[str, Any]) -> str:
    if not metadata:
        return ""

    lines = ["# Real AI Benchmark", ""]
    for key, value in metadata.items():
        if isinstance(value, Mapping):
            formatted_items = [
                f"{item_key}={item_value:.4f}" if isinstance(item_value, float) else f"{item_key}={item_value}"
                for item_key, item_value in value.items()
            ]
            formatted_value = ", ".join(formatted_items)
        else:
            formatted_value = str(value)
        lines.append(f"- {key}: {formatted_value}")
    lines.append("")
    return "\n".join(lines) + "\n"


async def run_seeded_genetic_weight_optimization(
    ga_config: GeneticAlgorithmConfig | None = None,
    fitness_config: SeededGeneticFitnessConfig | None = None,
) -> GeneticAlgorithmResult:
    """Train Level 3 weights with the real-coded GA using real seeded battles."""
    resolved_ga_config = ga_config or _default_seeded_ga_config()
    resolved_fitness_config = fitness_config or SeededGeneticFitnessConfig()
    battle_service = BattleService()
    ia_service = IAService()

    await _assert_seeded_data_available(battle_service)

    async def evaluate(chromosome: Chromosome) -> FitnessEvaluation:
        return await _evaluate_seeded_chromosome(chromosome, battle_service, ia_service, resolved_fitness_config)

    initial_population = [weight_mapping_to_chromosome(LEVEL_3_GA_OPTIMIZED_WEIGHTS)]
    return await RealCodedGeneticAlgorithm(evaluate, config=resolved_ga_config, initial_population=initial_population).run_async()


async def _run_single_seeded_battle(  # noqa: PLR0913
    *,
    battle_service: BattleService,
    ia_service: IAService,
    level_a: AILevel,
    level_b: AILevel,
    battle_type: BattleType,
    config: SeededBenchmarkConfig,
    level_a_weights: Mapping[str, float] | None = None,
    level_b_weights: Mapping[str, float] | None = None,
) -> SeededBattleResult:
    battle, instances = await _create_seeded_ai_battle(battle_service, level_a, level_b, battle_type)
    battle_id = str(battle.id)
    try:
        level_3_weights_by_trainer_id: dict[str, Mapping[str, float]] = {}
        if level_a == AI_LEVEL_HARD and level_a_weights is not None:
            level_3_weights_by_trainer_id["seeded-ai-a"] = level_a_weights
        if level_b == AI_LEVEL_HARD and level_b_weights is not None:
            level_3_weights_by_trainer_id["seeded-ai-b"] = level_b_weights

        reason = await _run_ai_loop_with_turn_limit(
            battle_service,
            ia_service,
            battle_id,
            config.max_turns,
            level_3_weights_by_trainer_id,
        )
        final_battle = await battle_service.get_battle(battle_id)
        final_instances = await _load_battle_instances(battle_id)
        winner_trainer_id = final_battle.result.winner_trainer_id if final_battle and final_battle.result else None
        winner_level = _resolve_winner_level(final_battle, winner_trainer_id) if final_battle and winner_trainer_id else None
        return SeededBattleResult(
            level_a=level_a,
            level_b=level_b,
            battle_type=battle_type,
            turns=final_battle.turn if final_battle else config.max_turns,
            winner_level=winner_level,
            winner_trainer_id=winner_trainer_id,
            remaining_hp_score=_team_remaining_hp(final_instances, winner_trainer_id),
            reason=reason,
        )
    finally:
        if config.cleanup_created_battles:
            await _delete_created_battle(battle, instances)


async def _create_seeded_ai_battle(
    battle_service: BattleService,
    level_a: AILevel,
    level_b: AILevel,
    battle_type: BattleType,
) -> tuple[Battle, list[BattleInstance]]:
    data = await battle_service.get_pokedex_data()
    team_size = int(battle_type[0])
    players = [
        Player(trainer_id="seeded-ai-a", name=f"AI A {AI_LEVEL_LABELS[level_a]}", controller_type="ai", ai_level=level_a),
        Player(trainer_id="seeded-ai-b", name=f"AI B {AI_LEVEL_LABELS[level_b]}", controller_type="ai", ai_level=level_b),
    ]
    battle, instances = await BattleSetupService.create_battle(
        battle_type=battle_type,
        players=players,
        team_size=team_size,
        movements=data["movements"],
        move_effects=data["move_effects"],
    )

    await battle.save()
    for instance in instances:
        await instance.save()
    return battle, instances


async def _run_ai_loop_with_turn_limit(
    battle_service: BattleService,
    ia_service: IAService,
    battle_id: str,
    max_turns: int,
    level_3_weights_by_trainer_id: Mapping[str, Mapping[str, float]] | None = None,
) -> str:
    while True:
        battle = await battle_service.get_battle(battle_id)
        if not battle:
            return "missing_battle"
        if battle.status == "finished":
            return battle.result.reason if battle.result else "finished"
        if battle.turn > max_turns:
            return "turn_limit"

        instances = await _load_battle_instances(battle_id)
        data = await battle_service.get_pokedex_data()
        actions = await _generate_ai_actions(
            ia_service,
            battle,
            instances,
            data["movements"],
            data["types"],
            level_3_weights_by_trainer_id,
        )
        if not actions:
            return "no_actions"

        if battle.phase == "awaiting_actions":
            await battle_service.execute_turn(battle_id, actions)
        elif battle.phase == "awaiting_replacements":
            await battle_service.execute_replacements(battle_id, actions)
        else:
            return f"unsupported_phase:{battle.phase}"


async def _generate_ai_actions(  # noqa: PLR0913
    ia_service: IAService,
    battle: Battle,
    instances: dict[str, BattleInstance],
    movements: dict,
    type_chart: dict,
    level_3_weights_by_trainer_id: Mapping[str, Mapping[str, float]] | None = None,
) -> list[TurnAction]:
    actions: list[TurnAction] = []
    for player in battle.players:
        if player.controller_type != "ai":
            continue

        if battle.phase == "awaiting_replacements":
            side = battle.sides.get(player.trainer_id)
            if side and any(slot is None for slot in side.active_pokemon_instance_ids):
                action = await ia_service.generate_switch_action(player, battle, instances, ai_level=player.ai_level or AI_LEVEL_EASY)
            else:
                action = None
        else:
            action = await ia_service.generate_action(
                player=player,
                battle=battle,
                instances=instances,
                ai_level=player.ai_level or AI_LEVEL_EASY,
                movements=movements,
                type_chart=type_chart,
                level_3_weights=(level_3_weights_by_trainer_id or {}).get(player.trainer_id),
            )

        if action:
            actions.append(action)
    return actions


async def _load_battle_instances(battle_id: str) -> dict[str, BattleInstance]:
    instances = await BattleInstance.find_many({"battleId": battle_id}).to_list()
    return {str(instance.id): instance for instance in instances}


async def _delete_created_battle(battle: Battle, instances: list[BattleInstance]) -> None:
    for instance in instances:
        await instance.delete()
    await battle.delete()


async def _assert_seeded_data_available(battle_service: BattleService) -> None:
    data = await battle_service.get_pokedex_data()
    if not data["movements"] or not data["move_effects"] or not data["types"]:
        raise RuntimeError(
            "Seeded benchmark requires moves, move_effects and type_chart data. Load frontend/pokemon.js into MongoDB first."
        )


def _resolve_winner_level(battle: Battle, winner_trainer_id: str) -> AILevel | None:
    player = next((candidate for candidate in battle.players if candidate.trainer_id == winner_trainer_id), None)
    return player.ai_level if player else None


def _team_remaining_hp(instances: dict[str, BattleInstance], trainer_id: str | None) -> float:
    if trainer_id is None:
        return 0.0
    team = [instance for instance in instances.values() if instance.trainer_id == trainer_id]
    max_hp = sum(instance.max_hp for instance in team)
    if max_hp <= 0:
        return 0.0
    return sum(max(0, instance.current_hp) for instance in team) / max_hp


def _summarize_results(
    level_a: AILevel,
    level_b: AILevel,
    battle_type: BattleType,
    results: list[SeededBattleResult],
) -> SeededBenchmarkSummary:
    wins_level_a = sum(1 for result in results if result.winner_level == level_a)
    wins_level_b = sum(1 for result in results if result.winner_level == level_b)
    draws = sum(1 for result in results if result.winner_level is None)
    average_turns = sum(result.turns for result in results) / len(results) if results else 0.0
    winner_hp_values = [result.remaining_hp_score for result in results if result.winner_level is not None]
    average_winner_hp = sum(winner_hp_values) / len(winner_hp_values) if winner_hp_values else 0.0
    return SeededBenchmarkSummary(
        level_a=level_a,
        level_b=level_b,
        battle_type=battle_type,
        battles=len(results),
        wins_level_a=wins_level_a,
        wins_level_b=wins_level_b,
        draws=draws,
        average_turns=average_turns,
        average_winner_hp=average_winner_hp,
    )


async def _evaluate_seeded_chromosome(
    chromosome: Chromosome,
    battle_service: BattleService,
    ia_service: IAService,
    config: SeededGeneticFitnessConfig,
) -> FitnessEvaluation:
    weights = chromosome_to_weight_mapping(chromosome)
    battle_config = SeededBenchmarkConfig(max_turns=config.max_turns, cleanup_created_battles=config.cleanup_created_battles)
    weighted_results: list[tuple[bool, SeededBattleResult]] = []

    for opponent_level in config.opponents:
        for battle_type in config.battle_types:
            for _ in range(config.matches_per_opponent):
                result_as_a = await _run_single_seeded_battle(
                    battle_service=battle_service,
                    ia_service=ia_service,
                    level_a=AI_LEVEL_HARD,
                    level_b=opponent_level,
                    battle_type=battle_type,
                    config=battle_config,
                    level_a_weights=weights,
                )
                weighted_results.append((result_as_a.winner_trainer_id == "seeded-ai-a", result_as_a))

                result_as_b = await _run_single_seeded_battle(
                    battle_service=battle_service,
                    ia_service=ia_service,
                    level_a=opponent_level,
                    level_b=AI_LEVEL_HARD,
                    battle_type=battle_type,
                    config=battle_config,
                    level_b_weights=weights,
                )
                weighted_results.append((result_as_b.winner_trainer_id == "seeded-ai-b", result_as_b))

    wins = sum(1 for won, _result in weighted_results if won)
    win_rate = wins / len(weighted_results) if weighted_results else 0.0
    winner_hp_values = [result.remaining_hp_score for won, result in weighted_results if won]
    hp_remaining_score = sum(winner_hp_values) / len(winner_hp_values) if winner_hp_values else 0.0
    average_turns = sum(result.turns for _won, result in weighted_results) / len(weighted_results) if weighted_results else 0.0
    turn_penalty = average_turns / max(1, config.max_turns)
    fitness = win_rate + (0.1 * hp_remaining_score) - (0.05 * turn_penalty)

    return FitnessEvaluation(
        fitness=fitness,
        win_rate=win_rate,
        hp_remaining_score=hp_remaining_score,
        average_turns=average_turns,
        speed_score=1.0 - turn_penalty,
        metadata={"weights": weights, "matches": len(weighted_results), "training": LEVEL_3_GA_TRAINING_METADATA},
    )


def _default_seeded_ga_config(seed: int | None = 42) -> GeneticAlgorithmConfig:
    return GeneticAlgorithmConfig(
        population_size=6,
        generations=4,
        elitism_count=1,
        tournament_size=3,
        crossover_rate=0.8,
        mutation_rate=0.15,
        mutation_std=0.05,
        matches_per_individual=6,
        seed=seed,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run real MongoDB-backed AI-vs-AI benchmarks.")
    parser.add_argument("--repetitions", type=int, default=int(os.getenv("REAL_AI_BENCHMARK_REPETITIONS", "1")))
    parser.add_argument("--max-turns", type=int, default=int(os.getenv("REAL_AI_BENCHMARK_MAX_TURNS", "80")))
    parser.add_argument("--output-dir", default=os.getenv("REAL_AI_BENCHMARK_OUTPUT_DIR", "benchmark-results"))
    parser.add_argument("--train-ga", action="store_true", help="Also run a small real-battle GA training pass.")
    parser.add_argument(
        "--save-trained-weights",
        action="store_true",
        help="Persist the trained GA weights into genetic_weights.py. Requires --train-ga.",
    )
    parser.add_argument(
        "--ga-battle-types",
        nargs="+",
        choices=DEFAULT_BATTLE_TYPES,
        default=("1v1",),
        help="Battle formats used during GA training. Benchmark output always includes 1v1, 2v2 and 3v3.",
    )
    parser.add_argument("--ga-population-size", type=int, default=6)
    parser.add_argument("--ga-generations", type=int, default=4)
    parser.add_argument("--ga-matches-per-opponent", type=int, default=1)
    return parser.parse_args()


async def _run_cli(args: argparse.Namespace) -> None:
    if args.save_trained_weights and not args.train_ga:
        raise ValueError("--save-trained-weights requires --train-ga")

    await init_db()
    trained_weights: dict[str, float] | None = None

    if args.train_ga:
        ga_result = await run_seeded_genetic_weight_optimization(
            ga_config=GeneticAlgorithmConfig(
                population_size=args.ga_population_size,
                generations=args.ga_generations,
                elitism_count=1,
                tournament_size=min(3, args.ga_population_size),
                seed=42,
            ),
            fitness_config=SeededGeneticFitnessConfig(
                battle_types=tuple(args.ga_battle_types),
                matches_per_opponent=args.ga_matches_per_opponent,
                max_turns=args.max_turns,
            ),
        )
        print("\nREAL SEEDED GA TRAINING")
        print(format_seeded_ga_history_table(ga_result))
        trained_weights = ga_result.weights
        print("\nPesos GA aprendidos que se usaran en el benchmark final:")
        print(json.dumps(trained_weights, indent=2, ensure_ascii=False))
        Path(args.output_dir).mkdir(parents=True, exist_ok=True)
        (Path(args.output_dir) / "level3_ga_training.json").write_text(
            json.dumps(ga_result.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if args.save_trained_weights:
            saved_path = save_level_3_weights(trained_weights, ga_result)
            print(f"\nPesos GA persistidos en: {saved_path}")

    summaries = await run_seeded_ai_benchmark(
        SeededBenchmarkConfig(
            repetitions_per_side=args.repetitions,
            max_turns=args.max_turns,
            cleanup_created_battles=True,
            level_3_weights=trained_weights,
        )
    )
    print("\nREAL SEEDED AI BENCHMARK")
    if trained_weights is not None:
        print("Benchmark final usando los pesos GA recien aprendidos.")
    print(format_seeded_benchmark_table(summaries))
    written_paths = write_seeded_benchmark_reports(
        summaries,
        args.output_dir,
        metadata={
            "level_3_weights_source": "trained_this_run" if trained_weights is not None else "code_default",
            "level_3_weights": trained_weights or LEVEL_3_GA_OPTIMIZED_WEIGHTS,
        },
    )
    print("\nReportes guardados:")
    for report_type, path in written_paths.items():
        print(f"- {report_type}: {path}")


def main() -> None:
    """CLI entrypoint for real AI benchmark reports."""
    asyncio.run(_run_cli(_parse_args()))
