from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from typing import Dict
import logging
import json

# Set up logging
logger = logging.getLogger("uvicorn")

# Define the name of the module and the topics
SERVER_ID = "server"

# Initialize the router
router = APIRouter(prefix="/api")

# Dictionary to keep track of connected devices
connected_devices: Dict[str, WebSocket] = {}


@router.websocket("/ws/{id}")
async def websocket_endpoint(websocket: WebSocket, id: str):
    logger.info(f"New connection: {id}")
    await websocket.accept()

    if id == "server":
        # Check if the server is already connected
        if SERVER_ID in connected_devices:
            logger.error("Server is already connected.")
            await websocket.close()
            return

        logger.info("Server connected")
        connected_devices[id] = websocket
        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                message = await websocket.receive_text()
                logger.info(f"Server sent: {message}")

                try:
                    # Assuming the message is JSON formatted
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON format")
                    await websocket.send_json({"error": "Invalid JSON format."})
                    continue

                if data:
                    target_robot_id = data.get("target_robot_id")
                    if target_robot_id in connected_devices:
                        await connected_devices[target_robot_id].send_json(data)
                        logger.info(
                            f"Forwarded message to {target_robot_id}: {message}"
                        )
                    else:
                        logger.warning(f"Robot {target_robot_id} not connected.")
                else:
                    logger.warning("No data received from server.")

        except WebSocketDisconnect:
            logger.warning("Server disconnected")
            connected_devices.pop(id, None)

    else:
        # Check if the server is connected
        if SERVER_ID not in connected_devices:
            logger.error("Server is not connected. Cannot proceed.")
            # Send message to robot that server is not connected
            await websocket.send_json({"error": "Server is not connected. Please try again later."})
            await websocket.close()
            return

        logger.info(f"Robot connected: {id}")
        connected_devices[id] = websocket
        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                message = await websocket.receive_text()
                logger.info(f"{id} sent: {message}")

                try:
                    # Assuming the message is JSON formatted
                    data = json.loads(message)
                except json.JSONDecodeError:
                    logger.error("Invalid JSON format")
                    await websocket.send_json({"error": "Invalid JSON format."})
                    continue

                if data:
                    # Forward the message to the server
                    await connected_devices[SERVER_ID].send_json(data)
                    logger.info(f"Forwarded message to server: {message}")
                else:
                    logger.warning("No data received from robot.")
                    continue
        except WebSocketDisconnect:
            logger.warning(f"{id} disconnected")
            connected_devices.pop(id, None)
