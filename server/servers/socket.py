import logging
from typing import List
from flask_socketio import Namespace, SocketIO, emit, join_room
from flask import Flask, request
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
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

    def on_join(self, payload):
        """event listener when client joins a match"""
        event = JoinEvent(payload, request.sid)

        logging.info(
            f"Player {event.player_name} [{event.socket_id}] joining match: {event.match_id}"
        )

        join_room(event.match_id)
        self._emit_responses(self.__match_service.join(event))

    def on_leave(self, payload):
        """event listener when client leaves a match"""
        self._emit_responses(
            self.__match_service.leave(PlayerEvent(payload), request.sid)
        )

    def on_draw(self, payload):
        """event listener when client draws a card"""
        self._emit_responses(self.__match_service.draw(PlayerEvent(payload)))

    def on_bid(self, payload):
        """event listener when client bid trumps"""
        self._emit_responses(self.__match_service.bid(CardsEvent(payload)))

    def on_kitty(self, payload):
        """event listener when client hides kitty"""
        self._emit_responses(self.__match_service.kitty(CardsEvent(payload)))

    def on_play(self, payload):
        """event listener when client plays a card"""
        self._emit_responses(self.__match_service.play(CardsEvent(payload)))

    def on_next(self, payload):
        """event listener when client is ready for the next game"""
        self._emit_responses(self.__match_service.next(PlayerEvent(payload)))


def init_sockets(app: Flask, match_service: MatchService) -> SocketIO:
    socketio = SocketIO(
        app, cors_allowed_origins="*", logger=True, engineio_logger=False
    )
    socketio.on_namespace(MatchNamespace("/match", match_service))
    return socketio
