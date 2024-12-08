import logging
from typing import List
from flask_socketio import Namespace, SocketIO, emit, join_room, leave_room
from flask import Flask, request
from abstractions.requests import (
    DrawRequest,
    JoinRequest,
    KittyRequest,
    NextRequest,
    PlayRequest,
    BidRequest,
)
from abstractions.responses import SocketResponse
from services.match import MatchService


class MatchNamespace(Namespace):
    def __init__(self, namespace: str, match_service: MatchService):
        super(MatchNamespace, self).__init__(namespace)
        self.__match_service = match_service

    def _emit_responses(self, responses: List[SocketResponse] | SocketResponse | None):
        if responses is None:
            return

        if not isinstance(responses, list):
            responses = [responses]

        for response in responses:
            emit(
                response.event,
                response.json(),
                to=response.recipient,
                broadcast=response.broadcast,
                include_self=response.include_self,
            )

    def on_connected(self):
        """event listener when client connects to the server"""
        logging.info(f"Client {request.sid} has connected")

    def on_disconnected(self):
        """event listener when client disconnects to the server"""
        logging.info(f"Client {request.sid} has disconnected")

    def on_leave(self, player_name, match_id):
        """event listener when client leaves a match"""
        logging.info(
            f"Player {player_name} [{request.sid}] leaving match: {str(match_id)}"
        )
        leave_room(match_id)
        emit("leave", player_name, to=match_id, broadcast=True)

    def on_join(self, payload):
        """event listener when client joins a match"""
        join_request = JoinRequest(payload, request.sid)

        logging.info(
            f"Player {join_request.player_name} [{join_request.socket_id}] joining match: {join_request.match_id}"
        )

        join_room(join_request.match_id)
        self._emit_responses(self.__match_service.join(join_request))

    def on_draw(self, payload):
        """event listener when client draws a card"""
        self._emit_responses(self.__match_service.draw(DrawRequest(payload)))

    def on_bid(self, payload):
        """event listener when client bid trumps"""
        self._emit_responses(self.__match_service.bid(BidRequest(payload)))

    def on_kitty(self, payload):
        """event listener when client hides kitty"""
        self._emit_responses(self.__match_service.kitty(KittyRequest(payload)))

    def on_play(self, payload):
        """event listener when client plays a card"""
        self._emit_responses(self.__match_service.play(PlayRequest(payload)))

    def on_next(self, payload):
        """event listener when client is ready for the next game"""
        self._emit_responses(self.__match_service.next(NextRequest(payload)))


def initialize(app: Flask, match_service: MatchService) -> SocketIO:
    socketio = SocketIO(
        app, cors_allowed_origins="*", logger=True, engineio_logger=False
    )
    socketio.on_namespace(MatchNamespace("/match", match_service))
    return socketio
