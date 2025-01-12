from abstractions import Card, Cards, Cards_, Suit
from abstractions.responses import PlayerUpdate


class Order:
    def __init__(self, trump_rank: int) -> None:
        # Inputs
        self.__trump_rank = trump_rank

        # Private
        self.__trump_suit = Suit.JOKER
        self.__order: dict[tuple[Suit, int], int] = {}
        # Rank order 1, 13, ..., 2, except trump rank
        self.__all_ranks = [1, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        self.__all_ranks.remove(self.__trump_rank)
        self.reset(Suit.JOKER)

    def reset(self, trump_suit: Suit) -> None:
        self.__trump_suit = trump_suit
        non_trump_suits = [
            suit
            for suit in [Suit.SPADE, Suit.HEART, Suit.CLUB, Suit.DIAMOND]
            if suit != trump_suit
        ]

        self.__order.clear()
        order = 0

        # Jokers
        self.__order[(Suit.JOKER, 2)] = order
        order += 1
        self.__order[(Suit.JOKER, 1)] = order
        order += 1

        # Trump suit + rank
        if trump_suit != Suit.JOKER:
            self.__order[(trump_suit, self.__trump_rank)] = order
            order += 1

        # Trump rank
        for suit in non_trump_suits:
            self.__order[(suit, self.__trump_rank)] = order
        order += 1

        # Trump rank
        if trump_suit != Suit.JOKER:
            for rank in self.__all_ranks:
                self.__order[(trump_suit, rank)] = order
                order += 1

        # Others
        for rank in self.__all_ranks:
            for suit in non_trump_suits:
                self.__order[(suit, rank)] = order
            order += 1

    def of(self, card: Card) -> int:
        return self.__order[(card.suit, card.rank)]

    def is_trump(self, card: Card) -> bool:
        return (
            card.suit == Suit.JOKER
            or card.suit == self.__trump_suit
            or card.rank == self.__trump_rank
        )

    def cards_in_suit(self, cards: Cards, suit: Suit, trump_suit: bool) -> Cards:
        return [
            card
            for card in cards
            if (trump_suit and self.is_trump(card))
            or (not trump_suit and not self.is_trump(card) and card.suit == suit)
        ]

    def same(self, one: Card, two: Card) -> bool:
        return self.of(one) == self.of(two)


class Player:
    def __init__(self, pid: int, name: str, sid: str, hand: Cards_ = None) -> None:
        # Inputs
        self.__hand = hand or []
        self.pid = pid
        self.name = name
        self.sid = sid

        # Public
        self.level = 2

    def update(self) -> PlayerUpdate:
        return PlayerUpdate(self.pid, self.name, self.level)

    def draw(self, cards: Cards) -> None:
        self.__hand.extend(cards)

    # If non-empty cards is passed in, checks if the player has the specified cards.
    # If cards is empty, checks if the player has any cards in hand.
    def has_cards(self, cards: Cards_ = None) -> bool:
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

    def cards_in_suit(self, order: Order, suit: Suit, include_trumps: bool) -> Cards:
        return order.cards_in_suit(self.__hand, suit, include_trumps)

    # Always call has_cards before calling play
    def play(self, cards: Cards) -> None:
        card_ids = set([card.id for card in cards])
        self.__hand = [card for card in self.__hand if card.id not in card_ids]
