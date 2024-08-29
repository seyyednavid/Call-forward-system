import logging
from appContents import app
from appContents.models import Settings
from appContents.config import Config 
import json
import websockets
import threading
import asyncio
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Log level
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log format
    handlers=[
        logging.FileHandler("websocket.log"),  # Log to a file in the root directory
        logging.StreamHandler()  # Also log to the console
    ]
)

logger = logging.getLogger(__name__)

# Variable to store number of cashiers (0-23)
called_position = 0

# Store a set of connected websocket clients
connected_clients = set()

async def hex_to_rgb(hex):
    """Convert hexadecimal color code to RGB tuple."""
    return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))

async def close_connection(websocket, reason):
    """Helper function to close the websocket connection and remove the client."""
    await websocket.close()
    if websocket in connected_clients:
        connected_clients.remove(websocket)
    logger.info(f"Client {websocket} removed due to {reason}. Total clients: {len(connected_clients)}")

async def handle_client(websocket, path):
    """Handle WebSocket client connections and messages."""
    global called_position
    # Add the client to the set of connected clients
    connected_clients.add(websocket)
    logger.info(f"New client connected. Total clients: {len(connected_clients)}")

    try:
        while True:
            # Wait for a message from the client
            message_json = await websocket.recv()

            if message_json:
                try:
                    # Parse JSON message
                    message_data = json.loads(message_json)
                    logger.info(f"----------------------------------------------------------------------------------")
                    logger.info("Received message: %s", message_data)

                    # Validate the ws_id field
                    if message_data.get("ws_id") != "Tensator_Websocket_server":
                        logger.warning("ws_id mismatch")
                        await close_connection(websocket, "ws_id mismatch")
                        break

                    # Validate the cb_id field
                    if message_data.get("cb_id") != "CB_123456789":
                        logger.warning("cb_id mismatch")
                        await close_connection(websocket, "cb_id mismatch")
                        break

                    if message_data.get("device_type") == "Edgelit-button":
                        egdelit_id = int(message_data["cmd_info"]["target"])
                        called_position = egdelit_id
                        event = message_data["cmd_info"]["event"]

                        with app.app_context():
                            data_in_db = Settings.query.filter_by(id=egdelit_id).first()

                            if data_in_db:
                                message_data["cmd_info"]["flash_speed"] = int(data_in_db.flashspeededgelit)
                                message_data["cmd_info"]["no_of_flashes"] = int(data_in_db.numofflashes)
                                message_data["cmd_info"]["on_color"] = await hex_to_rgb(data_in_db.on_color)
                                message_data["cmd_info"]["off_color"] = await hex_to_rgb(data_in_db.off_color)
                                message_data["cmd_info"]["free_color"] = await hex_to_rgb(data_in_db.free_color)
                                message_data["cmd_info"]["busy_color"] = await hex_to_rgb(data_in_db.busy_color)
                                logger.info(f"The message prepared to be sent: {message_data}")
                                
                                # Introduce a delay of 5ms before sending the message to clients
                                await asyncio.sleep(0.005)
                                
                                # Send message to all connected clients
                                for client in connected_clients:
                                    await client.send(json.dumps(message_data))
                                logger.info(f"----------------------------------------------------------------------------------")
                            else:
                                logger.warning(f"No data found in the database for edgelit_id: {egdelit_id}")
                                await close_connection(websocket, "No data in DB for edgelit_id")
                                break

                    elif message_data.get("device_type") in ["MG-button", "WiFi_CRED"]:
                        # Send message to all connected clients
                        for client in connected_clients:
                            await client.send(json.dumps(message_data))

                    else:
                        logger.warning("Device type mismatch")
                        await close_connection(websocket, "Device type mismatch")
                        break

                except json.JSONDecodeError:
                    logger.error("Error decoding JSON message")
                    await close_connection(websocket, "Error decoding JSON message")
                    break

    except websockets.exceptions.ConnectionClosed:
        connected_clients.remove(websocket)
        logger.info(f"Client {websocket} disconnected. Total clients: {len(connected_clients)}")

class WebSocketServerThread(threading.Thread):
    """Manage the WebSocket server thread."""
    def __init__(self):
        super().__init__()
        self.running = True
        self.server = None  # Variable to store the server instanc
        self.serve_forever_task = None  #  Variable to store the serve_forever task

    def terminate(self):
        """Terminate the WebSocket server thread."""
        self.running = False
        if self.server:
            # Close the server
            self.server.close() 
            asyncio.run_coroutine_threadsafe(self.serve_forever_task.cancel(), asyncio.get_event_loop())
            asyncio.get_event_loop().run_until_complete(self.server.wait_closed())  # Wait for server to close

    def run(self):
        """Run the WebSocket server."""
        while self.running:
            asyncio.set_event_loop(asyncio.new_event_loop())
            self.server = websockets.serve(handle_client, Config.FLASK_IP_ADDRESS, Config.WEBSOCKET_PORT)
            self.serve_forever_task = asyncio.ensure_future(self.server)
            asyncio.get_event_loop().run_until_complete(self.serve_forever_task)
            asyncio.get_event_loop().run_forever()