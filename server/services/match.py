from itertools import count
from typing import Dict, Iterator, Sequence
from abstractions.responses import MatchResponse, SocketResponse
from abstractions.requests import (
    DrawRequest,
    JoinRequest,
    KittyRequest,
    NextRequest,
    PlayRequest,
    BidRequest,
)
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

    def join(self, request: JoinRequest) -> Sequence[SocketResponse]:
        if request.match_id in self.__matches:
            return self.__matches[request.match_id].join(request)

    def draw(self, request: DrawRequest) -> Sequence[SocketResponse]:
        if request.match_id in self.__matches:
            return self.__matches[request.match_id].draw(request)

    def bid(self, request: BidRequest) -> SocketResponse | None:
        if request.match_id in self.__matches:
            return self.__matches[request.match_id].bid(request)

    def kitty(self, request: KittyRequest) -> Sequence[SocketResponse]:
        if request.match_id in self.__matches:
            return self.__matches[request.match_id].kitty(request)

    def play(self, request: PlayRequest) -> SocketResponse | None:
        if request.match_id in self.__matches:
            return self.__matches[request.match_id].play(request)

    def next(self, request: NextRequest) -> SocketResponse | None:
        if request.match_id in self.__matches:
            return self.__matches[request.match_id].next(request)
