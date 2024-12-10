from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from typing import Dict
from datetime import datetime, timedelta
import chess
import uuid
from dataclasses import dataclass, field
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class GameState:
    game_id: str
    board: chess.Board
    white_player: str = None
    black_player: str = None
    current_turn: str = "white"
    status: str = "waiting"  # waiting, ongoing, finished
    start_time: datetime = field(default_factory=datetime.utcnow)

    def elapsed_time(self) -> str:
        now = datetime.utcnow()
        elapsed = now - self.start_time
        total_seconds = int(elapsed.total_seconds())  # Convert to total seconds
        hours, remainder = divmod(total_seconds, 3600)  # Calculate hours
        minutes, seconds = divmod(remainder, 60)  # Calculate minutes and seconds
        return f"{hours:02}:{minutes:02}:{seconds:02}"


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}  # game_id -> {player_id: websocket}
        self.games: Dict[str, GameState] = {}

    async def connect(self, websocket: WebSocket, game_id: str, player_id: str):
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}
        self.active_connections[game_id][player_id] = websocket

        # Initialize game if it doesn't exist
        if game_id not in self.games:
            self.games[game_id] = GameState(game_id=game_id, board=chess.Board())

        # Assign player color
        game = self.games[game_id]
        if game.white_player is None:
            game.white_player = player_id
            print(f"Assigned White Player: {player_id}")
        elif game.black_player is None and player_id != game.white_player:
            game.black_player = player_id
            game.status = "ongoing"  # Start the game once both players are connected
            print(f"Assigned Black Player: {player_id}")

    def disconnect(self, game_id: str, player_id: str):
        if game_id in self.active_connections:
            self.active_connections[game_id].pop(player_id, None)
            if not self.active_connections[game_id]:  # No active connections
                del self.active_connections[game_id]
                del self.games[game_id]

    async def broadcast_game_state(self, game_id: str):
        if game_id in self.active_connections:
            game = self.games[game_id]
            message = {
                "type": "game_state",
                "data": {
                    "fen": game.board.fen(),
                    "current_turn": game.current_turn,
                    "status": game.status,
                    "white_player": game.white_player,
                    "black_player": game.black_player,
                    "legal_moves": [move.uci() for move in game.board.legal_moves],
                    "is_check": game.board.is_check(),
                    "is_checkmate": game.board.is_checkmate(),
                    "is_stalemate": game.board.is_stalemate(),
                    "time_elapsed": game.elapsed_time(),
                },
            }
            for connection in self.active_connections[game_id].values():
                await connection.send_json(message)

    async def broadcast_periodic_updates(self):
        while True:
            for game_id in list(self.games.keys()):  # Iterate over active games
                await self.broadcast_game_state(game_id)
            await asyncio.sleep(1)  # Send updates every 1 seconds


manager = ConnectionManager()

@app.on_event("startup")
async def start_periodic_updates():
    asyncio.create_task(manager.broadcast_periodic_updates())


@app.websocket("/ws/{game_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, player_id: str):
    await manager.connect(websocket, game_id, player_id)
    try:
        await manager.broadcast_game_state(game_id)

        while True:
            data = await websocket.receive_json()
            game = manager.games[game_id]

            if data["type"] == "move":
                # Verify it's the player's turn
                is_white = player_id == game.white_player
                if (is_white and game.current_turn == "white") or (not is_white and game.current_turn == "black"):
                    try:
                        move = chess.Move.from_uci(data["move"])
                        if move in game.board.legal_moves:
                            game.board.push(move)
                            game.current_turn = "black" if game.current_turn == "white" else "white"

                            if game.board.is_game_over():
                                game.status = "finished"

                            await manager.broadcast_game_state(game_id)
                        else:
                            await websocket.send_json({"type": "error", "message": "Invalid move"})
                    except ValueError:
                        await websocket.send_json({"type": "error", "message": "Invalid move"})
                else:
                    await websocket.send_json({"type": "error", "message": "Not your turn"})
    except WebSocketDisconnect:
        manager.disconnect(game_id, player_id)
        await manager.broadcast_game_state(game_id)


@app.get("/new-game")
async def create_game():
    game_id = str(uuid.uuid4())
    return {"game_id": game_id}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
