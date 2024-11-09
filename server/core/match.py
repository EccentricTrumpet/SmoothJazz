from itertools import count
from typing import Iterator, List, Sequence
from abstractions.enums import MatchPhase, Suit
from abstractions.types import Card, Player
from abstractions.requests import (
    DrawRequest,
    JoinRequest,
    KittyRequest,
    PlayRequest,
    TrumpRequest,
)
from abstractions.responses import (
    DrawResponse,
    JoinResponse,
    KittyResponse,
    MatchResponse,
    SocketResponse,
    TrumpResponse,
)
from .game import Game


class Match:
    def __init__(
        self,
        id: int,
        debug: bool = False,
        num_players: int = 4,
    ) -> None:
        self.__id = id
        self.__debug = debug
        self.__num_players = num_players

        # Monotonically increasing ids
        self.__player_id: Iterator[int] = count()

        # Private
        self.__phase = MatchPhase.CREATED
        # 1 deck for every 2 players, rounded down
        self.__num_cards = 54 * (self.__num_players // 2)
        self.__games: List[Game] = []
        self.__players: List[Player] = []

    def response(self) -> MatchResponse:
        return MatchResponse(
            self.__id,
            self.__debug,
            self.__num_players,
            self.__players,
        )

    def __add_player(self, name: str, socket_id: str) -> JoinResponse:
        player_id = next(self.__player_id)
        new_player = Player(player_id, name, socket_id, [])
        self.__players.append(new_player)
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

        if self.__debug and len(self.__players) == 1:
            for i in range(len(self.__players), self.__num_players):
                responses.append(self.__add_player(f"Mock{i}", request.socket_id))

        # Start the game if all players have joined
        if len(self.__players) == self.__num_players:
            new_game = Game(
                len(self.__games), self.__id, self.__num_cards, 2, 0, self.__players
            )
            self.__games.append(new_game)
            responses.append(new_game.start())
            self.__phase = MatchPhase.STARTED

        return responses

    def draw(self, request: DrawRequest) -> Sequence[DrawResponse]:
        response = self.__games[-1].draw(request)

        if response == None:
            return []

        if self.__debug:
            return [response]
        else:
            # Send a full response to the player who drew the card and broadcast
            # a response without card suit and rank to everyone else
            return [
                response,
                DrawResponse(
                    self.__id,
                    response.player_id,
                    response.phase,
                    response.activePlayerId,
                    [Card(card.id, Suit.UNKNOWN, 0) for card in response.cards],
                    broadcast=True,
                ),
            ]

    def trump(self, request: TrumpRequest) -> TrumpResponse | None:
        return self.__games[-1].trump(request)

    def kitty(self, request: KittyRequest) -> Sequence[KittyResponse]:
        response = self.__games[-1].kitty(request)

        if response == None:
            return []

        if self.__debug:
            return [response]
        else:
            # Send a full response to the player who drew the card and broadcast
            # a response without card suit and rank to everyone else
            return [
                response,
                KittyResponse(
                    self.__id,
                    response.player_id,
                    response.phase,
                    [Card(card.id, Suit.UNKNOWN, 0) for card in response.cards],
                    broadcast=True,
                ),
            ]

    def play(self, request: PlayRequest) -> Sequence[SocketResponse]:
        return self.__games[-1].play(request)
