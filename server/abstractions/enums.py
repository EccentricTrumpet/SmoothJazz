from enum import IntEnum, StrEnum


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
