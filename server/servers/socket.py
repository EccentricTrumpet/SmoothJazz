import logging
from flask_socketio import Namespace, SocketIO, emit, join_room
from flask import Flask, request
from abstractions import Room
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
from services.match import MatchService


class MatchNamespace(Namespace):
    def __init__(self, namespace: str, service: MatchService):
        super(MatchNamespace, self).__init__(namespace)
        self.__service = service

    def __update(self, room: Room | None):
        if room is not None:
            for update in room:
                emit(
                    update.name,
                    update.json(),
                    to=update.recipient,
                    broadcast=update.broadcast,
                    include_self=update.include_self,
                )

    def on_connected(self):
        """event listener when client connects to the server"""
        logging.info(f"Client {request.sid} has connected")

    def on_disconnected(self):
        """event listener when client disconnects to the server"""
        logging.info(f"Client {request.sid} has disconnected")

    def on_join(self, payload):
        """event listener when client joins a match"""
        event = JoinEvent(request.sid, payload)

        logging.info(
            f"Player {event.player_name} [{event.sid}] joining match: {event.match_id}"
        )

        join_room(event.match_id)
        self.__update(self.__service.join(event))

    def on_leave(self, payload):
        """event listener when client leaves a match"""
        self.__update(self.__service.leave(PlayerEvent(request.sid, payload)))

    def on_draw(self, payload):
        """event listener when client draws a card"""
        self.__update(self.__service.draw(PlayerEvent(request.sid, payload)))

    def on_bid(self, payload):
        """event listener when client bid trumps"""
        self.__update(self.__service.bid(CardsEvent(request.sid, payload)))

    def on_kitty(self, payload):
        """event listener when client hides kitty"""
        self.__update(self.__service.kitty(CardsEvent(request.sid, payload)))

    def on_play(self, payload):
        """event listener when client plays a card"""
        self.__update(self.__service.play(CardsEvent(request.sid, payload)))

    def on_next(self, payload):
        """event listener when client is ready for the next game"""
        self.__update(self.__service.next(PlayerEvent(request.sid, payload)))


def init_sockets(app: Flask, match_service: MatchService) -> SocketIO:
    socketio = SocketIO(
        app, cors_allowed_origins="*", logger=True, engineio_logger=False
    )
    socketio.on_namespace(MatchNamespace("/match", match_service))
    return socketio
