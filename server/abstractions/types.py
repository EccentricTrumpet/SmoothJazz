from typing import TypeVar
from abstractions.enums import Suit


TCard = TypeVar("TCard", bound="Card")


class Card:
    def __init__(self, id: int, suit: Suit, rank: int):
        self.id = id
        self.suit = suit
        self.rank = rank

    def is_equivalent_to(self, card: TCard) -> bool:
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
