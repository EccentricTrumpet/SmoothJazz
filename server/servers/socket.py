import logging

from abstractions import CardsEvent, JoinEvent, PlayerEvent, Room
from flask import Flask, request
from flask_socketio import Namespace, SocketIO, emit, join_room
from services.match import MatchService


class MatchNamespace(Namespace):
    def __init__(self, namespace: str, service: MatchService) -> None:
        super(MatchNamespace, self).__init__(namespace)
        self.__service = service

    def __update(self, room: Room | None) -> None:
        for update in room or []:
            emit(
                update.name,
                update.json(),
                to=update.to,
                broadcast=update.cast,
                include_self=update.echo,
            )

    def on_connected(self) -> None:
        """event listener when client connects to the server"""
        logging.info(f"Client {request.sid} has connected")

    def on_disconnected(self) -> None:
        """event listener when client disconnects to the server"""
        logging.info(f"Client {request.sid} has disconnected")

    def on_join(self, payload) -> None:
        """event listener when client joins a match"""
        event = JoinEvent(request.sid, payload)
        join_room(event.match_id)
        self.__update(self.__service.join(event))

    def on_leave(self, payload) -> None:
        """event listener when client leaves a match"""
        self.__update(self.__service.leave(PlayerEvent(request.sid, payload)))

    def on_draw(self, payload) -> None:
        """event listener when client draws a card"""
        self.__update(self.__service.draw(PlayerEvent(request.sid, payload)))

    def on_bid(self, payload) -> None:
        """event listener when client bid trumps"""
        self.__update(self.__service.bid(CardsEvent(request.sid, payload)))

    def on_kitty(self, payload) -> None:
        """event listener when client hides kitty"""
        self.__update(self.__service.kitty(CardsEvent(request.sid, payload)))

    def on_play(self, payload) -> None:
        """event listener when client plays a card"""
        self.__update(self.__service.play(CardsEvent(request.sid, payload)))

    def on_next(self, payload) -> None:
        """event listener when client is ready for the next game"""
        self.__update(self.__service.next(PlayerEvent(request.sid, payload)))


def init_sockets(app: Flask, match_service: MatchService) -> SocketIO:
    socketio = SocketIO(app, cors_allowed_origins="*", logger=True)
    socketio.on_namespace(MatchNamespace("/match", match_service))
    return socketio
