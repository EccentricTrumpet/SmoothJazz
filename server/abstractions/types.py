from typing import List, Sequence
from abstractions.enums import Suit


class Card:
    def __init__(self, id: int, suit: Suit, rank: int):
        self.id = id
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"[ Card ({self.id}) - {self.suit} {self.rank} ]"


class Player:
    def __init__(
        self,
        id: int,
        name: str,
        socket_id: str,
        hand: List[Card] = [],
    ) -> None:
        self.id = id
        self.name = name
        self.socket_id = socket_id
        self.__hand = hand

    def draw(self, cards: Sequence[Card]) -> None:
        self.__hand.extend(cards)
