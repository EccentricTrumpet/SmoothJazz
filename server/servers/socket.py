import logging
from flask_socketio import Namespace, SocketIO, emit
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


def initialize(app: Flask) -> SocketIO:
    socketio = SocketIO(
        app, cors_allowed_origins="*", logger=True, engineio_logger=False
    )
    socketio.on_namespace(ChatNamespace("/chat"))
    return socketio
