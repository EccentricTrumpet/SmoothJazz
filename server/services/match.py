from itertools import count
from typing import Dict, Iterator, Sequence
from abstractions.messages import (
    DrawRequest,
    JoinRequest,
    SocketResponse,
    MatchResponse,
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
        return new_match.current_state()

    def join(self, request: JoinRequest) -> Sequence[SocketResponse]:
        # TODO: Handle match not found
        return self.__matches[request.match_id].join(request)

    def draw(self, request: DrawRequest) -> Sequence[SocketResponse]:
        return self.__matches[request.match_id].draw(request)
