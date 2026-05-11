from fastapi import WebSocket


class ConnectionManager:
    print("Initializing ConnectionManager")  # Debug statement

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        print(
            "ConnectionManager initialized with empty active_connections"
        )  # Debug statement

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(
            f"User {user_id} connected. Total connections: {len(self.active_connections)}"
        )  # Debug statement

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)
        print(
            f"User {user_id} disconnected. Total connections: {len(self.active_connections)}"
        )  # Debug statement

    async def send_personal_message(
        self,
        user_id: str,
        message: dict,
    ):
        websocket = self.active_connections.get(user_id)

        if websocket:
            await websocket.send_json(message)
        print(f"Sent message to user {user_id}: {message}")  # Debug statement


manager = ConnectionManager()
