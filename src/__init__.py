from flask import Flask, session, url_for
from flask_socketio import SocketIO, join_room, leave_room, emit

import start
import game
from objects.Room import Room

class Config:
    SECRET_KEY = "dev"
    USERNAMES: set[str] = set()
    ROOMS: dict[str, Room] = {}

app = Flask(__name__)
app.config.from_object(Config)

app.register_blueprint(start.bp)
app.register_blueprint(game.bp)

socket = SocketIO(app)

usernames: set[str] = app.config["USERNAMES"]
rooms: dict[str, Room] = app.config["ROOMS"]

@socket.on("connect")
def handle_connect(_):
    roomName = session.get("roomName")
    username = session.get("userId")
    join_room(username)

    if roomName not in rooms:
        return
    
    room = rooms[roomName]

    if room.getWaiting():
        app.logger.info("Adding player1 to socket room")
        join_room(roomName)
        
    else:
        app.logger.info("Adding Player2 to socket room and starting game")
        join_room(roomName)
        emit("you", "", to=room.getTurn())
        emit("opponent", "", to=room.getNotTurn())
    

    app.logger.info(f"Client connected with userId {session.get('userId')}")

@socket.on("turn")
def turn(move):
    
    username = session.get("userId")
    roomName = session.get("roomName")
    room = rooms[roomName]
    moves = room.checkTurn(move, username)
    if moves:
        app.logger.info("Turn possible, switching whose turn it is")
        room.switchTurn()
        for x in moves:
            emit("you", x, to=room.getTurn())
            emit("opponent", x, to=room.getNotTurn())

        done = room.getDone()
        if done == "mate":
            emit("alert", f"{username} won the game!", to=roomName)
        if done == "stale":
            emit("alert", "It's a stalemate!", to=roomName)
    else:
        app.logger.info("Turn not possible")


@socket.on("disconnect")
def handle_disconnect():
    username = session.get("userId")
    roomName = session.get("roomName")
    session.clear()

    usernames.remove(username)
    leave_room(roomName)

    if roomName in rooms:
        rooms.pop(roomName)
    
    emit("alert", f"{username} disconnected.", to=roomName)

    app.logger.info(f"Client {username} disconnected")

@socket.on("getOpponent")
def get_opponent():
    username = session.get("userId")
    roomName = session.get("roomName")
    room = rooms[roomName]
    player1 = room.getPlayer1()
    player2 = room.getPlayer2()

    emit("opponentName", player1 if username == player2 else player2)

@socket.on("message")
def handle_message(data):
    app.logger.info(f"Got message from {session.get('userId')} containing {data}")
    

if __name__ == "__main__":
    socket.run(app, debug=True)