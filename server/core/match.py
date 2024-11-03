from itertools import count
from typing import Iterator, List, Sequence
from abstractions.enums import MatchPhase
from abstractions.types import Player
from abstractions.messages import (
    GameStartResponse,
    JoinRequest,
    JoinResponse,
    SocketResponse,
)
from .game import Game


class Match:
    def __init__(
        self,
        id: int,
        debug: bool = False,
        num_players: int = 4,
    ) -> None:
        # Private
        self.__id = id
        self.__debug = debug
        self.__phase = MatchPhase.CREATED
        self.__games: List[Game] = []

        # Monotonically increasing ids
        self.__player_id: Iterator[int] = count()

        # Public
        self.num_players = num_players
        self.players: List[Player] = []

    def __add_player(self, name: str, socket_id: str) -> JoinResponse:
        player_id = next(self.__player_id)
        new_player = Player(player_id, name, socket_id)
        self.players.append(new_player)
        return JoinResponse(self.__id, new_player.id, new_player.name)

    def join(self, request: JoinRequest) -> Sequence[JoinResponse]:
        responses: List[SocketResponse] = []

        # Do not process join request if match if full or ended
        if self.__phase == MatchPhase.STARTED or self.__phase == MatchPhase.ENDED:
            return responses

        # Assert request match_id matches id
        assert (
            request.match_id == self.__id
        ), f"Invalid Join Request to Match {self.__id}: {request}"

        responses.append(self.__add_player(request.player_name, request.socket_id))

        if self.__debug and len(self.players) == 1:
            for i in range(len(self.players), self.num_players):
                responses.append(self.__add_player(f"Mock{i}", request.socket_id))

        if len(self.players) == self.num_players:
            new_game = Game(self.__id, self.players, 0, 2)
            self.__games.append(new_game)
            responses.append(
                GameStartResponse(self.__id, new_game.current_player_id, new_game.deck)
            )
            self.__phase = MatchPhase.STARTED

        return responses
