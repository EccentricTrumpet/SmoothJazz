from enum import IntEnum, StrEnum
from typing import Self


class TrumpType(IntEnum):
    NONE = 0
    SINGLE = 1
    PAIR = 2
    SMALL_JOKER = 3
    BIG_JOKER = 4


class Suit(StrEnum):
    SPADE = "S"
    HEART = "H"
    CLUB = "C"
    DIAMOND = "D"
    JOKER = "J"
    UNKNOWN = "U"


class MatchPhase(IntEnum):
    CREATED = 0
    STARTED = 1
    PAUSED = 2
    ENDED = 3


class GamePhase(IntEnum):
    DRAW = 0
    RESERVE = 1  # 抓底牌
    KITTY = 2  # 埋底牌
    PLAY = 3
    END = 4


class Card:
    def __init__(self, id: int, suit: Suit, rank: int):
        self.id = id
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        return (
            isinstance(other, Card)
            and self.id == other.id
            and self.suit == other.suit
            and self.rank == other.rank
        )

    def matches(self, card: Self) -> bool:
        return self.suit == card.suit and self.rank == card.rank

    @property
    def points(self) -> int:
        if self.rank == 5:
            return 5
        if self.rank == 10 or self.rank == 13:
            return 10
        return 0

    def __str__(self):
        return f"[ Card ({self.id}) - {self.suit} {self.rank} ]"
