from abstractions import GamePhase, MatchPhase, PlayerError, Room
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
from abstractions.responses import MatchResponse, MatchUpdate
from core import BOSS_LEVELS
from core.game import Game
from core.players import Players


class Match:
    def __init__(self, id: int, debug: bool, num_players: int = 4) -> None:
        # Inputs
        self.__id = id
        self.__debug = debug
        self.__num_players = num_players

        # Private
        self.__phase = MatchPhase.CREATED
        self.__games: list[Game] = []

        # Public
        self.players = Players()

        # 1 deck for every 2 players, rounded down
        self.__num_decks = self.__num_players // 2

    def __add_player(self, name: str, sid: str, room: Room) -> None:
        room.public("join", self.players.add(name, sid).update())

    def __ensure_cards(self, event: CardsEvent) -> None:
        if not self.players[event.pid].has_cards(event.cards):
            raise PlayerError("Invalid cards", "You don't have those cards.")

    def response(self) -> MatchResponse:
        return MatchResponse(
            self.__id,
            self.__debug,
            self.__num_players,
            self.__phase,
            self.players.updates(),
        )

    def join(self, event: JoinEvent, room: Room) -> None:
        # Do not process join event if match if full or ended
        if self.__phase == MatchPhase.STARTED or self.__phase == MatchPhase.ENDED:
            return

        self.__add_player(event.player_name, event.sid, room)

        # Add mock players for debug mode
        if self.__debug and len(self.players) == 1:
            for i in range(len(self.players), self.__num_players):
                self.__add_player(f"Mock{i}", event.sid, room)

        # Start the game if all players have joined
        if len(self.players) == self.__num_players:
            # In the first game, the bidder is the kitty player
            new_game = Game(self.__num_decks, self.players, bid_team=True)
            self.__games.append(new_game)
            self.__phase = MatchPhase.STARTED
            room.public("start", new_game.start())
            room.public("match", MatchUpdate(self.__phase))

    def leave(self, event: PlayerEvent, room: Room) -> None:
        # Only allow players to leave a match that hasn't started
        if self.__phase != MatchPhase.CREATED:
            raise PlayerError("Cannot leave", "You can't leave after starting a match.")

        if event.pid in self.players:
            room.public("leave", self.players.remove(event.pid).update())

    def draw(self, event: PlayerEvent, room: Room) -> None:
        self.__games[-1].draw(event, room)

    def bid(self, event: CardsEvent, room: Room) -> None:
        self.__ensure_cards(event)
        self.__games[-1].bid(event, room)

    def kitty(self, event: CardsEvent, room: Room) -> None:
        self.__ensure_cards(event)
        self.__games[-1].kitty(event, room)

    def play(self, event: CardsEvent, room: Room) -> None:
        self.__ensure_cards(event)
        game = self.__games[-1]
        game.play(event, room)
        if (
            game.phase == GamePhase.END
            and self.players[game.next_pid].level == BOSS_LEVELS[-1]
        ):
            self.__phase = MatchPhase.ENDED
            room.public("match", MatchUpdate(self.__phase))

    def next(self, event: PlayerEvent, room: Room) -> None:
        game = self.__games[-1]
        if self.__debug or game.ready(event.pid):
            new_game = Game(self.__num_decks, self.players, game.next_pid)
            self.__games.append(new_game)
            return room.public("start", new_game.start())
