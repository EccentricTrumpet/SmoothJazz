from typing import Sequence
from abstractions.enums import Suit
from abstractions.types import Card
from core.order import Order


class Player:
    def __init__(
        self,
        id: int,
        name: str,
        socket_id: str,
        hand: Sequence[Card],
    ) -> None:
        self.id = id
        self.name = name
        self.socket_id = socket_id
        self.level = 2
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

    def cards_in_suit(
        self, order: Order, suit: Suit, include_trumps: bool
    ) -> Sequence[Card]:
        return [
            card
            for card in self.__hand
            if (include_trumps and order.is_trump(card))
            or (not include_trumps and not order.is_trump(card) and card.suit == suit)
        ]

    # Always call has_cards before calling play
    def play(self, cards: Sequence[Card]) -> None:
        card_ids = set([card.id for card in cards])
        self.__hand = [card for card in self.__hand if card.id not in card_ids]

    def is_empty_handed(self) -> bool:
        return len(self.__hand) == 0

    def card_count(self):
        return len(self.__hand)
