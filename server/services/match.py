from itertools import count
from typing import Dict, Iterator

from abstractions import Room
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
from abstractions.responses import MatchResponse
from core.match import Match


class MatchService:
    def __init__(self) -> None:
        # Monotonically increasing ids
        self.__match_id: Iterator[int] = count()
        self.__matches: Dict[int, Match] = dict()

    def __get_room(self, event: PlayerEvent | CardsEvent) -> Room | None:
        if event.match_id not in self.__matches:
            return None

        players = self.__matches[event.match_id].players
        player = next((p for p in players if p.id == event.pid), None)

        if player is not None:
            return Room(event.match_id, event.sid)

    def create(self, debug: bool) -> MatchResponse:
        match_id = next(self.__match_id)
        new_match = Match(match_id, debug)
        self.__matches[match_id] = new_match
        return new_match.response()

    def get(self, match_id: int) -> MatchResponse | None:
        if match_id in self.__matches:
            return self.__matches[match_id].response()

    def join(self, event: JoinEvent) -> Room | None:
        if event.match_id in self.__matches:
            room = Room(event.match_id, event.sid)
            self.__matches[event.match_id].join(event, room)
            return room

    def leave(self, event: PlayerEvent) -> Room | None:
        if (room := self.__get_room(event)) is not None:
            self.__matches[event.match_id].leave(event, room)
            return room

    def draw(self, event: PlayerEvent) -> Room | None:
        if (room := self.__get_room(event)) is not None:
            self.__matches[event.match_id].draw(event, room)
            return room

    def bid(self, event: CardsEvent) -> Room | None:
        if (room := self.__get_room(event)) is not None:
            self.__matches[event.match_id].bid(event, room)
            return room

    def kitty(self, event: CardsEvent) -> Room | None:
        if (room := self.__get_room(event)) is not None:
            self.__matches[event.match_id].kitty(event, room)
            return room

    def play(self, event: CardsEvent) -> Room | None:
        if (room := self.__get_room(event)) is not None:
            self.__matches[event.match_id].play(event, room)
            return room

    def next(self, event: PlayerEvent) -> Room | None:
        if (room := self.__get_room(event)) is not None:
            self.__matches[event.match_id].next(event, room)
            return room
