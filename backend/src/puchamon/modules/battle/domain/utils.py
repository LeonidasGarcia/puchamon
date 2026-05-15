"""Utility functions for battle domain."""


def format_pokemon_name(name: str) -> str:
    """Format a Pokemon name to have capitalized first letter.

    Args:
        name: The pokemon name (e.g., "pikachu" or "PIKACHU")

    Returns:
        The formatted name with first letter capitalized (e.g., "Pikachu")
    """
    return name.lower().capitalize()
