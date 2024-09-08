import logging
from flask_socketio import Namespace, SocketIO, emit, join_room, leave_room
from flask import Flask, request


class ChatNamespace(Namespace):
    def on_connected(self):
        """event listener when client connects to the server"""
        logging.info(f"client {request.sid} has connected")

    def on_data(self, data):
        """event listener when client types a message"""
        logging.info(f"client {request.sid} sent data: {str(data)}")
        emit("data", {"data": data, "id": request.sid}, broadcast=True)

    def on_disconnected(self):
        """event listener when client disconnects to the server"""
        logging.info(f"client {request.sid} has disconnected")


class MatchNamespace(Namespace):
    def on_connected(self):
        """event listener when client connects to the server"""
        logging.info(f"client {request.sid} has connected")

    def on_disconnected(self):
        """event listener when client disconnects to the server"""
        logging.info(f"client {request.sid} has disconnected")

    def on_join(self, player_name, match_id):
        """event listener when client joins a match"""
        logging.info(f"client {request.sid} joining match: {str(match_id)}")
        join_room(match_id)
        emit("join", player_name, to=match_id, broadcast=True)

    def on_leave(self, player_name, match_id):
        """event listener when client leaves a match"""
        logging.info(f"client {request.sid} leaving match: {str(match_id)}")
        leave_room(match_id)
        emit("leave", player_name, to=match_id, broadcast=True)

    def on_data(self, data, match_id):
        """event listener when client types a message"""
        logging.info(f"client {request.sid} sent data: {str(data)}")
        emit("data", data, to=match_id, broadcast=True)


def initialize(app: Flask) -> SocketIO:
    socketio = SocketIO(
        app, cors_allowed_origins="*", logger=True, engineio_logger=False
    )
    socketio.on_namespace(ChatNamespace("/chat"))
    socketio.on_namespace(MatchNamespace("/match"))
    return socketio
