from itertools import count
from typing import Dict, Iterator, Sequence
from abstractions.responses import SocketResponse
from abstractions.requests import (
    DrawRequest,
    JoinRequest,
    KittyRequest,
    TrumpRequest,
)
from core.match import Match


class MatchService:
    def __init__(self) -> None:
        # Monotonically increasing ids
        self.__match_id: Iterator[int] = count()
        self.__matches: Dict[int, Match] = dict()

    def create(self, debug: bool) -> SocketResponse:
        match_id = next(self.__match_id)
        new_match = Match(match_id, debug)
        self.__matches[match_id] = new_match
        return new_match.response()

    def join(self, request: JoinRequest) -> Sequence[SocketResponse]:
        # TODO: Handle match not found
        return self.__matches[request.match_id].join(request)

    def draw(self, request: DrawRequest) -> Sequence[SocketResponse]:
        # TODO: Handle match not found
        return self.__matches[request.match_id].draw(request)

    def trump(self, request: TrumpRequest) -> SocketResponse | None:
        # TODO: Handle match not found
        return self.__matches[request.match_id].trump(request)

    def kitty(self, request: KittyRequest) -> Sequence[SocketResponse]:
        # TODO: Handle match not found
        return self.__matches[request.match_id].kitty(request)
