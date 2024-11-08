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

    def has_cards(self, cards: Sequence[Card]) -> bool:
        card_ids = set([card.id for card in cards])

        # Ensure all cards in sequence are unique
        if len(card_ids) != len(cards):
            return False

        # Ensure all cards exist in hand
        if len(card_ids - set([card.id for card in self.__hand])) > 0:
            return False

        return True

    # Always call has_cards before calling play
    def play(self, cards: Sequence[Card]) -> None:
        card_ids = set([card.id for card in cards])
        self.__hand = [card for card in cards if card.id not in card_ids]
