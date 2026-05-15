"""Router for battle-related endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/battle", tags=["Battle"])
