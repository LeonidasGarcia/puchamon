"""WebSocket API for handling battle-related communications."""

from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ...agentia.application.services import IAService
from ..application.dto.battle_turn_dto import BattleTurnDTO
from ..application.mappers.battle_snapshot_mapper import to_battle_snapshot_dto
from ..application.services.battle_service import BattleService
from ..domain.entities.battle import TargetScope
from .schemas import ConnectionRequest, TurnSubmit

router = APIRouter(tags=["Battle"])

_current_websocket: WebSocket | None = None
_current_trainer_id: str | None = None
_current_battle_id: str | None = None
_current_controller_type: str | None = None
_battle_service: BattleService | None = None
_ia_service: IAService | None = None


def _get_battle_service() -> BattleService:
    global _battle_service
    if _battle_service is None:
        _battle_service = BattleService()
    return _battle_service


def _get_ia_service() -> IAService:
    global _ia_service
    if _ia_service is None:
        _ia_service = IAService()
    return _ia_service


def _create_initial_turn_dto(battle, instances) -> BattleTurnDTO:
    snapshot = to_battle_snapshot_dto(battle, instances)
    return BattleTurnDTO(
        battle_id=str(battle.id),
        turn=battle.turn,
        declared_actions=[],
        executed_actions=[],
        events=[],
        fainted_instance_ids=[],
        required_replacements=[],
        post_turn_snapshot=snapshot,
    )


async def _send_json(ws: WebSocket, data: dict[str, Any]) -> None:
    await ws.send_json(data)


async def _handle_connection_request(ws: WebSocket, payload: ConnectionRequest) -> None:
    global _current_trainer_id, _current_battle_id, _current_controller_type

    service = _get_battle_service()

    battle, instances = await service.create_battle(
        trainer_name=payload.name,
        controller_type=payload.controller_type,
        battle_type=payload.battle_type,
        difficulty=payload.difficulty or 1,
    )

    _current_trainer_id = battle.players[0].trainer_id
    _current_battle_id = str(battle.id)
    _current_controller_type = payload.controller_type

    initial_state = _create_initial_turn_dto(battle, instances)

    response = {
        "address": "connection:response",
        "payload": {
            "trainer_id": _current_trainer_id,
            "battle_id": _current_battle_id,
            "battle_type": battle.battle_type,
            "team_size": int(battle.battle_type[0]),
            "initial_state": initial_state.model_dump(),
        },
    }
    await _send_json(ws, response)

    if _current_controller_type == "ai":
        await _run_ai_vs_ai_loop(ws)


async def _run_ai_vs_ai_loop(ws: WebSocket) -> None:
    global _current_battle_id

    service = _get_battle_service()

    while True:
        battle = await service.get_battle(_current_battle_id)
        if not battle or battle.status == "finished":
            break

        result = await service.process_ai_turn(_current_battle_id)

        await _send_json(ws, {
            "address": "turn:result",
            "payload": result["turn_data"].model_dump(),
        })

        battle = await service.get_battle(_current_battle_id)


async def _handle_turn_submit(ws: WebSocket, payload: TurnSubmit) -> None:
    global _current_trainer_id, _current_battle_id, _current_controller_type

    if _current_controller_type != "human":
        return

    service = _get_battle_service()

    action_data = payload.action.model_dump()
    target_data = action_data.get("target")
    target = TargetScope(**target_data) if target_data else None
    action_dict = {
        "player": payload.trainer_id,
        "type": action_data["type"],
        "user_instance_id": action_data["user_instance_id"],
        "move_id": action_data.get("move_id"),
        "target": target,
        "replacement_instance_id": action_data.get("replacement_instance_id"),
    }
    action = type("TurnAction", (), action_dict)()

    result = await service.submit_action(
        battle_id=_current_battle_id,
        trainer_id=payload.trainer_id,
        action=action,
    )

    if result is None:
        return

    turn_data = result.get("turn_data")
    if turn_data:
        await _send_json(ws, {
            "address": "turn:result",
            "payload": turn_data.model_dump() if hasattr(turn_data, "model_dump") else turn_data,
        })
    else:
        await _send_json(ws, {
            "address": "turn:result",
            "payload": result,
        })


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Handle WebSocket connection for battle communication."""
    await ws.accept()

    try:
        while True:
            data = await ws.receive_json()
            address = data.get("address")
            payload = data.get("payload", {})

            if address == "connection:request":
                connection_req = ConnectionRequest(**payload)
                await _handle_connection_request(ws, connection_req)
            elif address == "turn:submit":
                turn_req = TurnSubmit(**payload)
                await _handle_turn_submit(ws, turn_req)
            elif address == "ping":
                await ws.send_json({"address": "pong"})
            else:
                await ws.send_json({
                    "address": "error",
                    "payload": {
                        "code": "INVALID_ADDRESS",
                        "message": f"Unknown address: {address}",
                    }
                })
    except WebSocketDisconnect:
        pass
