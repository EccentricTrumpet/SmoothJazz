from itertools import count
from typing import Iterator, List, Sequence
from abstractions import Card, GamePhase, MatchPhase, Suit
from abstractions.constants import END_LEVEL
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
from abstractions.responses import (
    AlertUpdate,
    DrawResponse,
    KittyResponse,
    MatchUpdate,
    MatchResponse,
    SocketUpdate,
    PlayerUpdate,
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

    def __add_player(self, name: str, socket_id: str) -> PlayerUpdate:
        player_id = next(self.__player_id)
        player = Player(player_id, name, socket_id, [])
        self.__players.append(player)
        return PlayerUpdate("join", self.__id, player.id, player.name, player.level)

    def join(self, event: JoinEvent) -> Sequence[PlayerUpdate]:
        responses: Sequence[SocketUpdate] = []

        # Do not process join event if match if full or ended
        if self.__phase == MatchPhase.STARTED or self.__phase == MatchPhase.ENDED:
            return responses

        # Assert event match_id matches id
        assert (
            event.match_id == self.__id
        ), f"Invalid join event to match {self.__id}: {event}"

        responses.append(self.__add_player(event.player_name, event.socket_id))

        # Add mock players for debug mode
        if self.__debug and len(self.__players) == 1:
            for i in range(len(self.__players), self.__num_players):
                responses.append(self.__add_player(f"Mock{i}", event.socket_id))

        # Start the game if all players have joined
        if len(self.__players) == self.__num_players:
            new_game = Game(
                len(self.__games), self.__id, self.__num_decks, self.__players
            )
            self.__games.append(new_game)
            responses.append(new_game.start())
            self.__phase = MatchPhase.STARTED
            responses.append(MatchUpdate(self.__id, self.__phase))

        return responses

    def leave(self, event: PlayerEvent, sid: str) -> SocketUpdate | None:
        # Only allow players to leave a match that hasn't started
        if self.__phase != MatchPhase.CREATED:
            return

        # Ensure the event came from the corresponding player
        if self.__players[event.player_id].socket_id != sid:
            return

        self.__players = [p for p in self.__players if p.id != event.player_id]

        return PlayerUpdate("leave", self.__id, event.player_id)

    def draw(self, event: PlayerEvent) -> Sequence[SocketUpdate] | SocketUpdate:
        response = self.__games[-1].draw(event)

        if self.__debug or isinstance(response, AlertUpdate):
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

    def bid(self, event: CardsEvent) -> SocketUpdate:
        return self.__games[-1].bid(event)

    def kitty(self, event: CardsEvent) -> SocketUpdate:
        response = self.__games[-1].kitty(event)

        if self.__debug or isinstance(response, AlertUpdate):
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

    def play(self, event: CardsEvent) -> Sequence[SocketUpdate]:
        game = self.__games[-1]
        responses = [game.play(event)]
        if (
            game.phase == GamePhase.END
            and self.__players[game.next_lead_id].level == END_LEVEL
        ):
            self.__phase = MatchPhase.ENDED
            responses.append(MatchUpdate(self.__id, self.__phase))
        return responses

    def next(self, event: CardsEvent) -> SocketUpdate | None:
        current_game = self.__games[-1]
        if self.__debug or current_game.ready(event.player_id):
            new_game = Game(
                len(self.__games),
                self.__id,
                self.__num_decks,
                self.__players,
                current_game.next_lead_id,
            )
            self.__games.append(new_game)
            return new_game.start()
