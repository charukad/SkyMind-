import asyncio
from fastapi import WebSocket
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class AlertManager:
    """
    Manages active WebSocket connections to push real-time alerts
    to the frontend Command Center.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """
        Pushes a High Risk or Threshold alert to all connected dashboard users.
        """
        message = json.dumps(alert_data)
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                self.disconnect(connection)

# Global instance to be used across the app
alert_manager = AlertManager()

async def evaluate_risk_threshold(flight_id: str, probability_delayed: float, explanation: Dict[str, Any]):
    """
    Core alerting logic. To be called by the inference engine or ingestion jobs.
    If the risk exceeds an operational threshold (e.g. > 75%), broadcast an immediate alert.
    """
    WARNING_THRESHOLD = 0.75
    
    if probability_delayed >= WARNING_THRESHOLD:
        alert = {
            "type": "HIGH_DELAY_RISK",
            "flight_id": flight_id,
            "risk_score": probability_delayed,
            "top_factor": explanation.get("top_risk_factor", "Unknown"),
            "message": explanation.get("explanation", "High risk of schedule disruption.")
        }
        
        logger.warning(f"THRESHOLD BREACH: {flight_id} has {probability_delayed*100}% delay risk. Broadcasting alert.")
        await alert_manager.broadcast_alert(alert)
