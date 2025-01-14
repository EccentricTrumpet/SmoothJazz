from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Iterator, Self

type Cards = list[Card]


class Suit(StrEnum):
    SPADE = "S"
    HEART = "H"
    CLUB = "C"
    DIAMOND = "D"
    JOKER = "J"
    UNKNOWN = "U"


class Card:
    def __init__(self, id: int, suit: Suit, rank: int) -> None:
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

    def __str__(self) -> str:
        return f"[ Card ({self.id}) - {self.suit} {self.rank} ]"

    @property
    def points(self) -> int:
        if self.rank == 5:
            return 5
        if self.rank == 10 or self.rank == 13:
            return 10
        return 0

    def json(self, secret=False) -> dict:
        if secret:
            return {"id": self.id, "suit": Suit.UNKNOWN, "rank": 0}
        return {"id": self.id, "suit": self.suit, "rank": self.rank}

    def matches(self, card: Self) -> bool:
        return self.suit == card.suit and self.rank == card.rank


# HTTP
class Response(ABC):
    @abstractmethod
    def json(self) -> dict: ...


# Socket
class Event:
    def __init__(self, sid: str, payload: dict) -> None:
        self.sid = sid
        self.match_id = int(payload["matchId"])


class JoinEvent(Event):
    def __init__(self, sid: str, payload: dict) -> None:
        super().__init__(sid, payload)
        self.player_name: str = payload["playerName"]


class PlayerEvent(Event):
    def __init__(self, sid: str, payload: dict) -> None:
        super().__init__(sid, payload)
        self.pid = int(payload["playerId"])


class CardsEvent(PlayerEvent):
    def __init__(self, sid: str, payload: dict) -> None:
        super().__init__(sid, payload)
        self.cards = [
            Card(int(card["id"]), Suit(card["suit"]), int(card["rank"]))
            for card in payload["cards"]
        ]


class Update(ABC):
    @abstractmethod
    def json(self, secret: bool = False) -> dict: ...


class SocketUpdate:
    def __init__(self, name: str, to: str, info: Update, cast=False, echo=True) -> None:
        self.name = name
        self.to = to
        self.info = info
        self.cast = cast
        self.echo = echo

    def json(self) -> dict:
        return self.info.json(self.cast and not self.echo)


class Room(ABC):
    def __init__(self, event: Event) -> None:
        self.__room_id = event.match_id
        self.__sid = event.sid
        self.__updates: list[SocketUpdate] = []

    def __iter__(self) -> Iterator[SocketUpdate]:
        for update in self.__updates:
            yield update

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


class PlayerError(Update, Exception):
    def __init__(self, title: str, message: str, hint_cards: Cards = []) -> None:
        self._title = title
        self._message = message
        self._hint_cards = hint_cards

    def json(self, _=False) -> dict:
        return {
            "title": self._title,
            "message": self._message,
            "hintCards": [card.json() for card in self._hint_cards],
        }
