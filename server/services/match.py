from itertools import count
from typing import Dict, Iterator, Sequence
from abstractions.responses import MatchResponse, SocketResponse
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
from core.match import Match


class MatchService:
    def __init__(self) -> None:
        # Monotonically increasing ids
        self.__match_id: Iterator[int] = count()
        self.__matches: Dict[int, Match] = dict()

    def create(self, debug: bool) -> MatchResponse:
        match_id = next(self.__match_id)
        new_match = Match(match_id, debug)
        self.__matches[match_id] = new_match
        return new_match.response()

    def get(self, match_id: int) -> MatchResponse | None:
        if match_id in self.__matches:
            return self.__matches[match_id].response()

    def join(self, event: JoinEvent) -> Sequence[SocketResponse]:
        if event.match_id in self.__matches:
            return self.__matches[event.match_id].join(event)

    def leave(self, event: PlayerEvent, sid: str) -> SocketResponse | None:
        if event.match_id in self.__matches:
            return self.__matches[event.match_id].leave(event, sid)

    def draw(self, event: PlayerEvent) -> Sequence[SocketResponse] | SocketResponse:
        if event.match_id in self.__matches:
            return self.__matches[event.match_id].draw(event)

    def bid(self, event: CardsEvent) -> SocketResponse | None:
        if event.match_id in self.__matches:
            return self.__matches[event.match_id].bid(event)

    def kitty(self, event: CardsEvent) -> Sequence[SocketResponse]:
        if event.match_id in self.__matches:
            return self.__matches[event.match_id].kitty(event)

    def play(self, event: CardsEvent) -> Sequence[SocketResponse]:
        if event.match_id in self.__matches:
            return self.__matches[event.match_id].play(event)

    def next(self, event: PlayerEvent) -> SocketResponse | None:
        if event.match_id in self.__matches:
            return self.__matches[event.match_id].next(event)
