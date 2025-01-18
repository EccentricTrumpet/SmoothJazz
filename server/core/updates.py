from enum import IntEnum

from abstractions import Cards, Update
from core import Player
from core.players import Players


class MatchPhase(IntEnum):
    CREATED = 0
    STARTED = 1
    PAUSED = 2
    ENDED = 3


class GamePhase(IntEnum):
    DRAW = 0
    KITTY = 1  # 埋底牌
    PLAY = 2
    END = 3


class PlayerUpdate(Update):
    def __init__(self, player: Player) -> None:
        self.player = player

    def json(self, _=False) -> dict:
        return self.player.json()


class StartUpdate(Update):
    def __init__(self, active_pid: int, cards: int, rank: int) -> None:
        self.active_pid = active_pid
        self.cards = cards
        self.rank = rank

    def json(self, _=False) -> dict:
        return {"activePid": self.active_pid, "cards": self.cards, "rank": self.rank}


class TeamUpdate(Update):
    def __init__(self, kitty_pid: int, defenders: list[int]) -> None:
        self.kitty_pid = kitty_pid
        self.defenders = defenders

    def json(self, _=False) -> dict:
        return {"kittyPid": self.kitty_pid, "defenders": self.defenders}


class MatchUpdate(Update):
    def __init__(self, phase: MatchPhase) -> None:
        self.phase = phase

    def json(self, _=False) -> dict:
        return {"phase": self.phase}


class CardsUpdate(Update):
    def __init__(
        self,
        pid: int,
        cards: Cards,
        next_pid: int | None = None,
        hint_pid: int | None = None,
        phase: GamePhase | None = None,
        score: int | None = None,
    ) -> None:
        self.pid = pid
        self.next_pid = next_pid
        self.cards = cards
        self.hint_pid = hint_pid
        self.phase = phase
        self.score = score

    def json(self, secret=False) -> dict:
        json = {"pid": self.pid, "cards": [card.json(secret) for card in self.cards]}
        if self.next_pid is not None:
            json["nextPID"] = self.next_pid
        if self.hint_pid is not None:
            json["hintPID"] = self.hint_pid
        if self.phase is not None:
            json["phase"] = self.phase
        if self.score is not None:
            json["score"] = self.score
        return json


class EndUpdate(Update):
    def __init__(self, play: CardsUpdate, kitty: CardsUpdate, players: Players) -> None:
        self.play = play
        self.kitty = kitty
        self.players = players

    def json(self, _=False) -> dict:
        return {
            "play": self.play.json(),
            "kitty": self.kitty.json(),
            "players": self.players.json(),
        }
