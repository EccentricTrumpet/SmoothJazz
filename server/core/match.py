from itertools import count
from typing import Iterator, List, Sequence
from abstractions import Card, GamePhase, MatchPhase, Suit
from abstractions.constants import END_LEVEL
from abstractions.requests import (
    DrawRequest,
    JoinRequest,
    KittyRequest,
    LeaveRequest,
    PlayRequest,
    BidRequest,
)
from abstractions.responses import (
    AlertResponse,
    DrawResponse,
    JoinResponse,
    KittyResponse,
    LeaveResponse,
    MatchPhaseResponse,
    MatchResponse,
    SocketResponse,
)
from core import Player
from core.game import Game


class Match:
    def __init__(
        self,
        id: int,
        debug: bool = False,
        num_players: int = 4,
    ) -> None:
        # Inputs
        self.__id = id
        self.__debug = debug
        self.__num_players = num_players

        # Monotonically increasing ids
        self.__player_id: Iterator[int] = count()

        # Private
        self.__phase = MatchPhase.CREATED
        self.__games: List[Game] = []
        self.__players: List[Player] = []

        # 1 deck for every 2 players, rounded down
        self.__num_decks = self.__num_players // 2

    def response(self) -> MatchResponse:
        return MatchResponse(
            self.__id,
            self.__debug,
            self.__num_players,
            self.__phase,
            [(player.id, player.name, player.level) for player in self.__players],
        )

    def __add_player(self, name: str, socket_id: str) -> JoinResponse:
        player_id = next(self.__player_id)
        new_player = Player(player_id, name, socket_id, [])
        self.__players.append(new_player)
        return JoinResponse(self.__id, new_player.id, new_player.name, new_player.level)

    def join(self, request: JoinRequest) -> Sequence[JoinResponse]:
        responses: Sequence[SocketResponse] = []

        # Do not process join request if match if full or ended
        if self.__phase == MatchPhase.STARTED or self.__phase == MatchPhase.ENDED:
            return responses

        # Assert request match_id matches id
        assert (
            request.match_id == self.__id
        ), f"Invalid Join Request to Match {self.__id}: {request}"

        responses.append(self.__add_player(request.player_name, request.socket_id))

        # Add mock players for debug mode
        if self.__debug and len(self.__players) == 1:
            for i in range(len(self.__players), self.__num_players):
                responses.append(self.__add_player(f"Mock{i}", request.socket_id))

        # Start the game if all players have joined
        if len(self.__players) == self.__num_players:
            new_game = Game(
                len(self.__games), self.__id, self.__num_decks, self.__players
            )
            self.__games.append(new_game)
            responses.append(new_game.start())
            self.__phase = MatchPhase.STARTED
            responses.append(MatchPhaseResponse(self.__id, self.__phase))

        return responses

    def leave(self, request: LeaveRequest, sid: str) -> SocketResponse | None:
        # Only allow players to leave a match that hasn't started
        if self.__phase != MatchPhase.CREATED:
            return

        # Ensure the request came from the corresponding player
        if self.__players[request.player_id].socket_id != sid:
            return

        self.__players = [p for p in self.__players if p.id != request.player_id]

        return LeaveResponse(self.__id, request.player_id)

    def draw(self, request: DrawRequest) -> Sequence[SocketResponse] | SocketResponse:
        response = self.__games[-1].draw(request)

        if self.__debug or isinstance(response, AlertResponse):
            return response
        else:
            # Send a full response to the player who drew the card and broadcast
            # a response without card suit and rank to everyone else
            return [
                response,
                DrawResponse(
                    self.__id,
                    response.id,
                    response.phase,
                    response.activePlayerId,
                    [Card(card.id, Suit.UNKNOWN, 0) for card in response.cards],
                    broadcast=True,
                ),
            ]

    def bid(self, request: BidRequest) -> SocketResponse:
        return self.__games[-1].bid(request)

    def kitty(self, request: KittyRequest) -> SocketResponse:
        response = self.__games[-1].kitty(request)

        if self.__debug or isinstance(response, AlertResponse):
            return response
        else:
            # Send a full response to the player who hid the kitty and broadcast
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
        game = self.__games[-1]
        responses = [game.play(request)]
        if (
            game.phase == GamePhase.END
            and self.__players[game.next_lead_id].level == END_LEVEL
        ):
            self.__phase = MatchPhase.ENDED
            responses.append(MatchPhaseResponse(self.__id, self.__phase))
        return responses

    def next(self, request: PlayRequest) -> SocketResponse | None:
        current_game = self.__games[-1]
        if self.__debug or current_game.ready(request.player_id):
            new_game = Game(
                len(self.__games),
                self.__id,
                self.__num_decks,
                self.__players,
                current_game.next_lead_id,
            )
            self.__games.append(new_game)
            return new_game.start()
