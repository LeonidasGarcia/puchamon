"""Helpers for resolving immutable battle stats from pokedex data."""

from math import floor

from ....pokedex.domain.entities import Moveset, Pokemon
from ..entities import BattleStats
from ..exceptions import BattleValidationError
from ..rules import DEFAULT_BATTLE_IV, DEFAULT_BATTLE_LEVEL, MAX_EV_PER_STAT, MAX_TOTAL_EVS

_SUPPORTED_STAT_KEYS: tuple[str, ...] = ("hp", "atk", "def_", "spa", "spd", "spe")
_STAT_KEY_ALIASES: dict[str, str] = {"def": "def_"}
_MAX_IV = 31
_NATURE_EFFECTS: dict[str, tuple[str | None, str | None]] = {
    "hardy": (None, None),
    "lonely": ("atk", "def_"),
    "brave": ("atk", "spe"),
    "adamant": ("atk", "spa"),
    "naughty": ("atk", "spd"),
    "bold": ("def_", "atk"),
    "docile": (None, None),
    "relaxed": ("def_", "spe"),
    "impish": ("def_", "spa"),
    "lax": ("def_", "spd"),
    "timid": ("spe", "atk"),
    "hasty": ("spe", "def_"),
    "serious": (None, None),
    "jolly": ("spe", "spa"),
    "naive": ("spe", "spd"),
    "modest": ("spa", "atk"),
    "mild": ("spa", "def_"),
    "quiet": ("spa", "spe"),
    "bashful": (None, None),
    "rash": ("spa", "spd"),
    "calm": ("spd", "atk"),
    "gentle": ("spd", "def_"),
    "sassy": ("spd", "spe"),
    "careful": ("spd", "spa"),
    "quirky": (None, None),
}


def _normalize_stat_key(stat_key: str) -> str:
    """Normalize stat keys coming from movesets and payloads."""
    normalized_key = _STAT_KEY_ALIASES.get(stat_key, stat_key)
    if normalized_key not in _SUPPORTED_STAT_KEYS:
        raise BattleValidationError(f"Unsupported stat key '{stat_key}' for battle stat resolution")
    return normalized_key


def _require_base_stat(pokemon: Pokemon, stat_key: str) -> int:
    """Read a base stat from the Pokemon species data."""
    try:
        value = getattr(pokemon.base_stats, stat_key)
    except AttributeError as exc:
        raise BattleValidationError(f"Pokemon '{pokemon.id or pokemon.name}' is missing base stat '{stat_key}'") from exc

    if value <= 0:
        raise BattleValidationError(f"Pokemon '{pokemon.id or pokemon.name}' has invalid base stat '{stat_key}'={value}")
    return value


def _normalize_evs(moveset: Moveset) -> dict[str, int]:
    """Validate and normalize the EV spread stored in the moveset."""
    evs = {stat_key: 0 for stat_key in _SUPPORTED_STAT_KEYS}
    for raw_stat_key, raw_value in moveset.evs.items():
        stat_key = _normalize_stat_key(raw_stat_key)
        if raw_value < 0 or raw_value > MAX_EV_PER_STAT:
            raise BattleValidationError(f"Moveset '{moveset.id or moveset.moveset_name}' has invalid EV '{raw_stat_key}'={raw_value}")
        evs[stat_key] = raw_value

    if sum(evs.values()) > MAX_TOTAL_EVS:
        raise BattleValidationError(f"Moveset '{moveset.id or moveset.moveset_name}' exceeds the {MAX_TOTAL_EVS} EV limit")
    return evs


def _resolve_nature_multiplier(nature_name: str, stat_key: str) -> float:
    """Return the stat multiplier contributed by the nature."""
    normalized_nature = nature_name.strip().lower()
    try:
        raised_stat_key, lowered_stat_key = _NATURE_EFFECTS[normalized_nature]
    except KeyError as exc:
        raise BattleValidationError(f"Unsupported nature '{nature_name}' for battle stat resolution") from exc

    if stat_key == raised_stat_key:
        return 1.1
    return 0.9 if stat_key == lowered_stat_key else 1.0


def _calculate_hp_stat(*, base_stat: int, ev: int, level: int, iv: int) -> int:
    """Calculate HP using the standard Pokemon formula."""
    return floor(((2 * base_stat + iv + floor(ev / 4)) * level) / 100) + level + 10


def _calculate_non_hp_stat(*, base_stat: int, ev: int, level: int, iv: int, nature_multiplier: float) -> int:
    """Calculate a non-HP stat using the standard Pokemon formula."""
    value = floor(((2 * base_stat + iv + floor(ev / 4)) * level) / 100) + 5
    return floor(value * nature_multiplier)


def calculate_effective_stat(base_value: int, stages: int) -> int:
    """Calculate the effective stat after applying stages."""
    stages = max(-6, min(6, stages))
    numerator = max(2, 2 + stages)
    denominator = max(2, 2 - stages)
    return floor(base_value * numerator / denominator)


def build_battle_stats(*, pokemon: Pokemon, moveset: Moveset, level: int = DEFAULT_BATTLE_LEVEL, iv: int = DEFAULT_BATTLE_IV) -> BattleStats:
    """Build the immutable stats a Pokemon carries into battle."""
    if level <= 0:
        raise BattleValidationError(f"Battle stat resolution requires a positive level, got '{level}'")
    if iv < 0 or iv > _MAX_IV:
        raise BattleValidationError(f"Battle stat resolution requires IV values between 0 and 31, got '{iv}'")
    if pokemon.id is not None and moveset.pokemon_id != pokemon.id:
        raise BattleValidationError(f"Moveset '{moveset.id or moveset.moveset_name}' does not belong to pokemon '{pokemon.id or pokemon.name}'")

    evs = _normalize_evs(moveset)

    return BattleStats(
        hp=_calculate_hp_stat(base_stat=_require_base_stat(pokemon, "hp"), ev=evs["hp"], level=level, iv=iv),
        atk=_calculate_non_hp_stat(
            base_stat=_require_base_stat(pokemon, "atk"),
            ev=evs["atk"],
            level=level,
            iv=iv,
            nature_multiplier=_resolve_nature_multiplier(moveset.nature, "atk"),
        ),
        def_=_calculate_non_hp_stat(
            base_stat=_require_base_stat(pokemon, "def_"),
            ev=evs["def_"],
            level=level,
            iv=iv,
            nature_multiplier=_resolve_nature_multiplier(moveset.nature, "def_"),
        ),
        spa=_calculate_non_hp_stat(
            base_stat=_require_base_stat(pokemon, "spa"),
            ev=evs["spa"],
            level=level,
            iv=iv,
            nature_multiplier=_resolve_nature_multiplier(moveset.nature, "spa"),
        ),
        spd=_calculate_non_hp_stat(
            base_stat=_require_base_stat(pokemon, "spd"),
            ev=evs["spd"],
            level=level,
            iv=iv,
            nature_multiplier=_resolve_nature_multiplier(moveset.nature, "spd"),
        ),
        spe=_calculate_non_hp_stat(
            base_stat=_require_base_stat(pokemon, "spe"),
            ev=evs["spe"],
            level=level,
            iv=iv,
            nature_multiplier=_resolve_nature_multiplier(moveset.nature, "spe"),
        ),
    )
