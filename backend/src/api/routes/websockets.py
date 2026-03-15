from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging
from src.services.alerts.manager import alert_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSockets"])

@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for frontend clients to subscribe to real-time risk alerts.
    """
    await alert_manager.connect(websocket)
    try:
        while True:
            # We don't expect the client to send much, mostly just keep-alive/ping
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        alert_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        alert_manager.disconnect(websocket)
