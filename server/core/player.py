from typing import Sequence
from abstractions import Card, Suit
from core.order import Order


# TODO: Extract interface to put into abstractions
class Player:
    def __init__(
        self,
        id: int,
        name: str,
        socket_id: str,
        hand: Sequence[Card],
    ) -> None:
        # Inputs
        self.__hand = hand
        self.id = id
        self.name = name
        self.socket_id = socket_id

        # Public
        self.level = 2

    def draw(self, cards: Sequence[Card]) -> None:
        self.__hand.extend(cards)

    # If non-empty cards is passed in, checks if the player has the specified cards.
    # If cards is empty, checks if the player has any cards in hand.
    def has_cards(self, cards: Sequence[Card] | None = None) -> bool:
        if cards is None:
            return len(self.__hand) > 0

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
        return order.cards_in_suit(self.__hand, suit, include_trumps)

    # Always call has_cards before calling play
    def play(self, cards: Sequence[Card]) -> None:
        card_ids = set([card.id for card in cards])
        self.__hand = [card for card in self.__hand if card.id not in card_ids]
