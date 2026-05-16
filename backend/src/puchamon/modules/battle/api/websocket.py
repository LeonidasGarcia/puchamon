"""WebSocket API for handling battle-related communications."""

import contextlib
from dataclasses import dataclass
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..domain.entities.battle import TargetScope
from ..domain.entities.battle import TurnAction as DomainTurnAction
from .dependencies import get_battle_coordinator_service, get_battle_service
from .schemas import ConnectionRequest, TurnSubmit

router = APIRouter(tags=["Battle"])


@dataclass
class ConnectionState:
    """Holds state for a single WebSocket connection."""

    trainer_id: str | None = None
    battle_id: str | None = None
    controller_type: str | None = None


async def _send_json(ws: WebSocket, data: dict[str, Any]) -> None:
    await ws.send_json(data)


async def _handle_connection_request(ws: WebSocket, payload: ConnectionRequest, state: ConnectionState) -> None:
    service = get_battle_service()

    battle, instances = await service.create_battle(
        trainer_name=payload.name,
        controller_type=payload.controller_type,
        battle_type=payload.battle_type,
        difficulty=payload.difficulty or 1,
    )

    state.trainer_id = battle.players[0].trainer_id
    state.battle_id = str(battle.id)
    state.controller_type = payload.controller_type

    initial_state_dto = await service.get_initial_state_dto(battle, instances)

    response = {
        "address": "connection:response",
        "payload": {
            "trainer_id": state.trainer_id,
            "battle_id": state.battle_id,
            "battle_type": battle.battle_type,
            "team_size": int(battle.battle_type[0]),
            "initial_state": initial_state_dto.model_dump(),
        },
    }
    await _send_json(ws, response)

    if state.controller_type == "ai":
        await _run_ai_vs_ai_loop(ws, state)


async def _run_ai_vs_ai_loop(ws: WebSocket, state: ConnectionState) -> None:
    if not state.battle_id:
        return

    coordinator = get_battle_coordinator_service()
    results = await coordinator.run_ai_vs_ai_loop(state.battle_id)

    for result in results:
        await _send_json(
            ws,
            {
                "address": "turn:result",
                "payload": result["turn_data"].model_dump(),
            },
        )


async def _handle_turn_submit(ws: WebSocket, payload: TurnSubmit, state: ConnectionState) -> None:
    if state.controller_type != "human" or not state.battle_id:
        return

    coordinator = get_battle_coordinator_service()

    target = TargetScope(**payload.action.target.model_dump()) if payload.action.target else None

    domain_action = DomainTurnAction(
        player=payload.trainer_id,
        type=payload.action.type,
        user_instance_id=payload.action.user_instance_id,
        move_id=payload.action.move_id,
        target=target,
        replacement_instance_id=payload.action.replacement_instance_id,
    )

    results = await coordinator.submit_human_action(
        battle_id=state.battle_id,
        trainer_id=payload.trainer_id,
        action=domain_action,
    )

    for result in results:
        if turn_data := result.get("turn_data"):
            await _send_json(
                ws,
                {
                    "address": "turn:result",
                    "payload": turn_data.model_dump() if hasattr(turn_data, "model_dump") else turn_data,
                },
            )
        else:
            await _send_json(
                ws,
                {
                    "address": "turn:result",
                    "payload": result,
                },
            )


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle WebSocket connection for battle communication."""
    await ws.accept()
    state = ConnectionState()

    with contextlib.suppress(WebSocketDisconnect):
        while True:
            data = await ws.receive_json()
            address = data.get("address")
            payload = data.get("payload", {})

            if address == "connection:request":
                connection_req = ConnectionRequest(**payload)
                await _handle_connection_request(ws, connection_req, state)
            elif address == "turn:submit":
                turn_req = TurnSubmit(**payload)
                await _handle_turn_submit(ws, turn_req, state)
            elif address == "ping":
                await ws.send_json({"address": "pong"})
            else:
                await ws.send_json(
                    {
                        "address": "error",
                        "payload": {
                            "code": "INVALID_ADDRESS",
                            "message": f"Unknown address: {address}",
                        },
                    }
                )
