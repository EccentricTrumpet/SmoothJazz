from abc import ABC, abstractmethod
from enum import IntEnum, StrEnum
from typing import Iterator, Optional, Self


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
    KITTY = 1  # 埋底牌
    PLAY = 2
    END = 3


class Card:
    def __init__(self, id: int, suit: Suit, rank: int):
        self.id = id
        self.suit = suit
        self.rank = rank

    def __eq__(self, other: object) -> bool:
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

    def __str__(self) -> str:
        return f"[ Card ({self.id}) - {self.suit} {self.rank} ]"


# HTTP responses
class HttpResponse(ABC):
    @abstractmethod
    def json(self) -> dict: ...


# Socket responses
class Update(ABC):
    @abstractmethod
    def json(self, secret: bool = False) -> dict: ...


class SocketUpdate:
    def __init__(
        self, name: str, to: str, update: Update, cast: bool = False, echo: bool = True
    ):
        self.name = name
        self.to = to
        self._update = update
        self.cast = cast
        self.echo = echo

    def json(self) -> dict:
        return self._update.json(self.cast and not self.echo)


class Room(ABC):
    def __init__(self, room_id: int, sid: str):
        self.__room_id = room_id
        self.__sid = sid
        self.__updates: list[SocketUpdate] = []
        self.__index = 0

    def __iter__(self) -> Iterator[SocketUpdate]:
        self.__index = 0
        return self

    def __next__(self) -> SocketUpdate:
        if self.__index < len(self.__updates):
            value = self.__updates[self.__index]
            self.__index += 1
            return value
        else:
            raise StopIteration

    @property
    def has_updates(self) -> bool:
        return len(self.__updates) > 0

    # Send a private update to the player
    def reply(self, name: str, update: Update) -> None:
        self.__updates.append(SocketUpdate(name, self.__sid, update))

    # Send a private update to the player and broadcast an anonymized update to the match
    def secret(self, name: str, update: Update) -> None:
        self.__updates.append(SocketUpdate(name, self.__sid, update))
        self.__updates.append(SocketUpdate(name, self.__room_id, update, True, False))

    # Broadcast a public update to the match
    def public(self, name: str, update: Update) -> None:
        self.__updates.append(SocketUpdate(name, self.__room_id, update, True))


Cards = list[Card]
Cards_ = Optional[Cards]
Room_ = Optional[Room]


class PlayerError(Update, Exception):
    def __init__(self, title: str, message: str, hint_cards: Cards = []):
        self._title = title
        self._message = message
        self._hint_cards = hint_cards

    def json(self, _: bool = False) -> dict:
        return {
            "title": self._title,
            "message": self._message,
            "hintCards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self._hint_cards
            ],
        }
