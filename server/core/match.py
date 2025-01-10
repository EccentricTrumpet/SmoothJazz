from itertools import count
from typing import Iterator, List
from abstractions import GamePhase, MatchPhase, Room
from abstractions.constants import BOSS_LEVELS
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
from abstractions.responses import MatchUpdate, MatchResponse, PlayerUpdate
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

        # Public
        self.players: List[Player] = []

        # 1 deck for every 2 players, rounded down
        self.__num_decks = self.__num_players // 2

    def response(self) -> MatchResponse:
        return MatchResponse(
            self.__id,
            self.__debug,
            self.__num_players,
            self.__phase,
            [(player.id, player.name, player.level) for player in self.players],
        )

    def __add_player(self, name: str, socket_id: str, room: Room) -> None:
        player_id = next(self.__player_id)
        player = Player(player_id, name, socket_id, [])
        self.players.append(player)
        room.public("join", PlayerUpdate(player.id, player.name, player.level))

    def join(self, event: JoinEvent, room: Room) -> None:

        # Do not process join event if match if full or ended
        if self.__phase == MatchPhase.STARTED or self.__phase == MatchPhase.ENDED:
            return

        # Assert event match_id matches id
        assert (
            event.match_id == self.__id
        ), f"Invalid join event to match {self.__id}: {event}"

        self.__add_player(event.player_name, event.sid, room)

        # Add mock players for debug mode
        if self.__debug and len(self.players) == 1:
            for i in range(len(self.players), self.__num_players):
                self.__add_player(f"Mock{i}", event.sid, room)

        # Start the game if all players have joined
        if len(self.players) == self.__num_players:
            new_game = Game(len(self.__games), self.__num_decks, self.players)
            self.__games.append(new_game)
            room.public("start", new_game.start())
            self.__phase = MatchPhase.STARTED
            room.public("phase", MatchUpdate(self.__phase))

    def leave(self, event: PlayerEvent, room: Room) -> None:
        # Only allow players to leave a match that hasn't started
        if self.__phase != MatchPhase.CREATED:
            return

        self.players = [p for p in self.players if p.id != event.player_id]
        room.public("leave", PlayerUpdate(event.player_id))

    def draw(self, event: PlayerEvent, room: Room) -> None:
        self.__games[-1].draw(event, room)

    def bid(self, event: CardsEvent, room: Room) -> None:
        self.__games[-1].bid(event, room)

    def kitty(self, event: CardsEvent, room: Room) -> None:
        self.__games[-1].kitty(event, room)

    def play(self, event: CardsEvent, room: Room) -> None:
        game = self.__games[-1]
        game.play(event, room)
        if (
            game.phase == GamePhase.END
            and self.players[game.next_lead_id].level == BOSS_LEVELS[-1]
        ):
            self.__phase = MatchPhase.ENDED
            room.public("phase", MatchUpdate(self.__phase))

    def next(self, event: CardsEvent, room: Room) -> None:
        current_game = self.__games[-1]
        if self.__debug or current_game.ready(event.player_id):
            new_game = Game(
                len(self.__games),
                self.__num_decks,
                self.players,
                current_game.next_lead_id,
            )
            self.__games.append(new_game)
            return room.public("start", new_game.start())
