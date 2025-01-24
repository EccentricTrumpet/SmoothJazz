from abstractions import CardsEvent, JoinEvent, PlayerError, PlayerEvent, Response, Room
from core import LEVELS
from core.game import Game
from core.players import Players
from core.updates import MatchPhase, MatchUpdate, PlayerUpdate


class MatchSettings:
    def __init__(self, json: dict) -> None:
        self.seats = json["seats"] if "seats" in json else 4
        self.debug = json["debug"] if "debug" in json else False
        self.logs = json["logs"] if "logs" in json else False

    def json(self) -> dict:
        return {
            "seats": self.seats,
            "debug": self.debug,
            "logs": self.logs,
        }


class MatchResponse(Response):
    def __init__(self, id: int, settings, players: Players) -> None:
        self.__id = id
        self.__settings = settings
        self.__players = players

    def json(self) -> dict:
        return {
            "id": self.__id,
            "settings": self.__settings.json(),
            "players": self.__players.json(),
        }


class Match:
    def __init__(self, id: int, settings: MatchSettings) -> None:
        # Inputs
        self.__id = id
        self.__settings = settings

        # Private
        self.__phase = MatchPhase.CREATED
        self.__games: list[Game] = []

        # Public
        self.players = Players()

    def __add_player(self, name: str, sid: str, room: Room) -> None:
        room.public("join", PlayerUpdate(self.players.add(name, sid)))

    def __ensure_cards(self, event: CardsEvent) -> None:
        if not self.players[event.pid].has_cards(event.cards):
            raise PlayerError("Invalid cards", "You don't have those cards.")

    def response(self) -> MatchResponse:
        return MatchResponse(self.__id, self.__settings, self.players)

    def join(self, event: JoinEvent, room: Room) -> None:
        # Do not process join event if match if full or ended
        if self.__phase == MatchPhase.STARTED or self.__phase == MatchPhase.ENDED:
            return

        self.__add_player(event.player_name, event.sid, room)

        # Add mock players for debug mode
        if self.__settings.debug and len(self.players) == 1:
            for i in range(len(self.players), self.__settings.seats):
                self.__add_player(f"Mock{i}", event.sid, room)

        # Start the game if all players have joined
        if len(self.players) == self.__settings.seats:
            # In the first game, the bidder is the kitty player
            new_game = Game(self.players, room, self.players.first().pid, True)
            self.__games.append(new_game)
            self.__phase = MatchPhase.STARTED
            room.public("match", MatchUpdate(self.__phase))

    def leave(self, event: PlayerEvent, room: Room) -> None:
        # Only allow players to leave a match that hasn't started
        if self.__phase != MatchPhase.CREATED:
            raise PlayerError("Cannot leave", "You can't leave after starting a match.")

        if event.pid in self.players:
            room.public("leave", PlayerUpdate(self.players.remove(event.pid)))

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
        if (next := game.next_pid) != -1 and self.players[next].level == LEVELS[-1]:
            self.__phase = MatchPhase.ENDED
            room.public("match", MatchUpdate(self.__phase))

    def next(self, event: PlayerEvent, room: Room) -> None:
        game = self.__games[-1]
        if self.__settings.debug or game.ready(event.pid):
            new_game = Game(self.players, room, game.next_pid)
            self.__games.append(new_game)
