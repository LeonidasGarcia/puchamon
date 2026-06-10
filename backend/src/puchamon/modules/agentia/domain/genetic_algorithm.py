"""Real-coded genetic algorithm for optimizing AI heuristic weights."""

import inspect
from collections.abc import Awaitable, Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from random import Random
from typing import Any

GENETIC_WEIGHT_NAMES = ("hp", "alive", "damage", "type", "speed", "status", "effects")
MIN_POPULATION_SIZE = 2
Chromosome = tuple[float, ...]
FitnessEvaluator = Callable[[Chromosome], "FitnessEvaluation | float | Awaitable[FitnessEvaluation | float]"]


@dataclass(frozen=True, slots=True)
class GeneticAlgorithmConfig:
    """Configuration for the real-coded genetic algorithm."""

    population_size: int = 10
    generations: int = 10
    elitism_count: int = 2
    tournament_size: int = 3
    crossover_rate: float = 0.8
    mutation_rate: float = 0.15
    mutation_std: float = 0.05
    matches_per_individual: int = 10
    seed: int | None = None

    def __post_init__(self) -> None:
        """Validate configuration values that would break evolution."""
        if self.population_size < MIN_POPULATION_SIZE:
            raise ValueError(f"population_size must be at least {MIN_POPULATION_SIZE}")
        if self.generations < 1:
            raise ValueError("generations must be at least 1")
        if self.elitism_count < 0 or self.elitism_count >= self.population_size:
            raise ValueError("elitism_count must be between 0 and population_size - 1")
        if self.tournament_size < 1 or self.tournament_size > self.population_size:
            raise ValueError("tournament_size must be between 1 and population_size")
        if not 0.0 <= self.crossover_rate <= 1.0:
            raise ValueError("crossover_rate must be between 0 and 1")
        if not 0.0 <= self.mutation_rate <= 1.0:
            raise ValueError("mutation_rate must be between 0 and 1")
        if self.mutation_std < 0.0:
            raise ValueError("mutation_std must be non-negative")
        if self.matches_per_individual < 1:
            raise ValueError("matches_per_individual must be at least 1")


@dataclass(frozen=True, slots=True)
class FitnessEvaluation:
    """Fitness metrics produced for one chromosome."""

    fitness: float
    win_rate: float = 0.0
    hp_remaining_score: float = 0.0
    average_turns: float = 0.0
    speed_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the evaluation for reports and API responses."""
        return {
            "fitness": self.fitness,
            "win_rate": self.win_rate,
            "hp_remaining_score": self.hp_remaining_score,
            "average_turns": self.average_turns,
            "speed_score": self.speed_score,
            "metadata": self.metadata,
        }


@dataclass(frozen=True, slots=True)
class EvaluatedIndividual:
    """Chromosome with its evaluated fitness metrics."""

    chromosome: Chromosome
    evaluation: FitnessEvaluation

    @property
    def fitness(self) -> float:
        """Return the scalar value used by selection."""
        return self.evaluation.fitness

    def to_dict(self) -> dict[str, Any]:
        """Serialize this individual for reports."""
        return {
            "weights": chromosome_to_weight_mapping(self.chromosome),
            "fitness": self.evaluation.fitness,
            "evaluation": self.evaluation.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class GenerationReport:
    """Summary of the best individual found in one generation."""

    generation: int
    best: EvaluatedIndividual
    average_fitness: float

    def to_dict(self) -> dict[str, Any]:
        """Serialize generation metrics for tabular output."""
        return {
            "generation": self.generation,
            "best": self.best.to_dict(),
            "average_fitness": self.average_fitness,
        }


@dataclass(frozen=True, slots=True)
class GeneticAlgorithmResult:
    """Final output of a genetic optimization run."""

    best: EvaluatedIndividual
    history: list[GenerationReport]
    config: GeneticAlgorithmConfig

    @property
    def weights(self) -> dict[str, float]:
        """Return the optimized normalized weights by factor name."""
        return chromosome_to_weight_mapping(self.best.chromosome)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the optimization result for reports."""
        return {
            "weights": self.weights,
            "fitness": self.best.evaluation.fitness,
            "win_rate": self.best.evaluation.win_rate,
            "hp_remaining_score": self.best.evaluation.hp_remaining_score,
            "average_turns": self.best.evaluation.average_turns,
            "generations": self.config.generations,
            "history": [entry.to_dict() for entry in self.history],
        }


def _evaluated_individual_fitness(individual: EvaluatedIndividual) -> float:
    """Return the scalar fitness value used to rank individuals."""
    return individual.fitness


def normalize_chromosome(values: Sequence[float]) -> Chromosome:
    """Clamp a real-coded chromosome to non-negative values and normalize it to sum 1."""
    if len(values) != len(GENETIC_WEIGHT_NAMES):
        raise ValueError(f"chromosome must have {len(GENETIC_WEIGHT_NAMES)} genes")

    cleaned_values = tuple(max(0.0, float(value)) for value in values)
    total = sum(cleaned_values)
    if total <= 0.0:
        equal_weight = 1.0 / len(GENETIC_WEIGHT_NAMES)
        return tuple(equal_weight for _ in GENETIC_WEIGHT_NAMES)
    return tuple(value / total for value in cleaned_values)


def chromosome_to_weight_mapping(chromosome: Sequence[float]) -> dict[str, float]:
    """Convert a chromosome into the named weight mapping used by the heuristic."""
    normalized = normalize_chromosome(chromosome)
    return dict(zip(GENETIC_WEIGHT_NAMES, normalized, strict=True))


def weight_mapping_to_chromosome(weights: Mapping[str, float]) -> Chromosome:
    """Convert named heuristic weights into a normalized chromosome."""
    return normalize_chromosome(tuple(weights.get(name, 0.0) for name in GENETIC_WEIGHT_NAMES))


class RealCodedGeneticAlgorithm:
    """Optimize normalized heuristic weights using tournament selection, crossover, mutation and elitism."""

    def __init__(
        self,
        fitness_evaluator: FitnessEvaluator,
        config: GeneticAlgorithmConfig | None = None,
        initial_population: Iterable[Sequence[float]] | None = None,
    ) -> None:
        self._fitness_evaluator = fitness_evaluator
        self._config = config or GeneticAlgorithmConfig()
        self._rng = Random(self._config.seed)
        self._initial_population = [normalize_chromosome(chromosome) for chromosome in initial_population or []]

        if len(self._initial_population) > self._config.population_size:
            raise ValueError("initial_population cannot be larger than population_size")

    def run(self) -> GeneticAlgorithmResult:
        """Run the complete genetic optimization and return the best chromosome found."""
        population = self._create_initial_population()
        history: list[GenerationReport] = []
        global_best: EvaluatedIndividual | None = None

        for generation in range(1, self._config.generations + 1):
            evaluated_population = self._evaluate_population(population)
            generation_best = evaluated_population[0]
            if global_best is None or generation_best.fitness > global_best.fitness:
                global_best = generation_best

            average_fitness = sum(individual.fitness for individual in evaluated_population) / len(evaluated_population)
            history.append(GenerationReport(generation=generation, best=generation_best, average_fitness=average_fitness))

            if generation < self._config.generations:
                population = self._build_next_generation(evaluated_population)

        if global_best is None:
            raise RuntimeError("genetic algorithm finished without evaluating a population")
        return GeneticAlgorithmResult(best=global_best, history=history, config=self._config)

    async def run_async(self) -> GeneticAlgorithmResult:
        """Run the complete genetic optimization with an async battle-backed evaluator."""
        population = self._create_initial_population()
        history: list[GenerationReport] = []
        global_best: EvaluatedIndividual | None = None

        for generation in range(1, self._config.generations + 1):
            evaluated_population = await self._evaluate_population_async(population)
            generation_best = evaluated_population[0]
            if global_best is None or generation_best.fitness > global_best.fitness:
                global_best = generation_best

            average_fitness = sum(individual.fitness for individual in evaluated_population) / len(evaluated_population)
            history.append(GenerationReport(generation=generation, best=generation_best, average_fitness=average_fitness))

            if generation < self._config.generations:
                population = self._build_next_generation(evaluated_population)

        if global_best is None:
            raise RuntimeError("genetic algorithm finished without evaluating a population")
        return GeneticAlgorithmResult(best=global_best, history=history, config=self._config)

    def _create_initial_population(self) -> list[Chromosome]:
        population = list(self._initial_population)
        while len(population) < self._config.population_size:
            population.append(normalize_chromosome(tuple(self._rng.random() for _ in GENETIC_WEIGHT_NAMES)))
        return population

    def _evaluate_population(self, population: list[Chromosome]) -> list[EvaluatedIndividual]:
        evaluated = [
            EvaluatedIndividual(
                chromosome=chromosome,
                evaluation=self._coerce_evaluation(self._fitness_evaluator(chromosome)),
            )
            for chromosome in population
        ]
        evaluated.sort(key=_evaluated_individual_fitness, reverse=True)
        return evaluated

    async def _evaluate_population_async(self, population: list[Chromosome]) -> list[EvaluatedIndividual]:
        evaluated: list[EvaluatedIndividual] = []
        for chromosome in population:
            evaluation = self._fitness_evaluator(chromosome)
            if inspect.isawaitable(evaluation):
                evaluation = await evaluation
            evaluated.append(EvaluatedIndividual(chromosome=chromosome, evaluation=self._coerce_evaluation(evaluation)))
        evaluated.sort(key=_evaluated_individual_fitness, reverse=True)
        return evaluated

    def _coerce_evaluation(self, value: FitnessEvaluation | float) -> FitnessEvaluation:
        if isinstance(value, FitnessEvaluation):
            return value
        return FitnessEvaluation(fitness=float(value))

    def _build_next_generation(self, evaluated_population: list[EvaluatedIndividual]) -> list[Chromosome]:
        next_generation = [individual.chromosome for individual in evaluated_population[: self._config.elitism_count]]

        while len(next_generation) < self._config.population_size:
            parent_a = self._select_parent(evaluated_population).chromosome
            parent_b = self._select_parent(evaluated_population).chromosome
            child = self._crossover(parent_a, parent_b)
            child = self._mutate(child)
            next_generation.append(child)

        return next_generation

    def _select_parent(self, evaluated_population: list[EvaluatedIndividual]) -> EvaluatedIndividual:
        contestants = self._rng.sample(evaluated_population, self._config.tournament_size)
        selected = contestants[0]
        for contestant in contestants[1:]:
            if contestant.fitness > selected.fitness:
                selected = contestant
        return selected

    def _crossover(self, parent_a: Chromosome, parent_b: Chromosome) -> Chromosome:
        if self._rng.random() > self._config.crossover_rate:
            return parent_a

        alpha = self._rng.random()
        return normalize_chromosome(tuple((alpha * gene_a) + ((1.0 - alpha) * gene_b) for gene_a, gene_b in zip(parent_a, parent_b, strict=True)))

    def _mutate(self, chromosome: Chromosome) -> Chromosome:
        mutated_genes = []
        for gene in chromosome:
            if self._rng.random() <= self._config.mutation_rate:
                mutated_genes.append(gene + self._rng.gauss(0.0, self._config.mutation_std))
            else:
                mutated_genes.append(gene)
        return normalize_chromosome(tuple(mutated_genes))
