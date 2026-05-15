"""Router for Pokedex-related endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/pokedex", tags=["Pokedex"])
