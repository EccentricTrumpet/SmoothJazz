from enum import IntEnum

from abstractions import Card, Cards, Suit

# Level 14 is Aces, Level 15 is the end level
LEVELS = [2, 5, 10, 13, 14, 15]
DECK_SIZE = 54
SUIT_SIZE = 13
KITTY_SIZE = 8
DECK_THRESHOLD = 20


class Trump(IntEnum):
    NONE = 0
    SINGLE = 1
    PAIR = 2
    SMALL_JOKER = 3
    BIG_JOKER = 4


class Order:
    SUITS = [Suit.SPADE, Suit.HEART, Suit.CLUB, Suit.DIAMOND]

    def __init__(self, level: int) -> None:
        # Public
        self.trump_suit = Suit.JOKER
        self.trump_rank = level - SUIT_SIZE if level > SUIT_SIZE else level

        # Private
        self.__order: dict[tuple[Suit, int], int] = {}
        # Rank order 1, 13, ..., 2, except trump rank
        self.__all_ranks = [1, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2]
        self.__all_ranks.remove(self.trump_rank)
        self.reset(Suit.JOKER)

    def reset(self, trump_suit: Suit) -> None:
        self.trump_suit = trump_suit
        non_trump_suits = [suit for suit in Order.SUITS if suit != trump_suit]

        self.__order.clear()
        order = 0

        # Jokers
        self.__order[(Suit.JOKER, 2)] = order
        order += 1
        self.__order[(Suit.JOKER, 1)] = order
        order += 1

        # Trump suit + rank
        if trump_suit != Suit.JOKER:
            self.__order[(trump_suit, self.trump_rank)] = order
            order += 1

        # Trump rank
        for suit in non_trump_suits:
            self.__order[(suit, self.trump_rank)] = order
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
            or card.suit == self.trump_suit
            or card.rank == self.trump_rank
        )

    def cards_in_suit(self, cards: Cards, suit: Suit, trump_suit: bool) -> Cards:
        if trump_suit:
            return [c for c in cards if self.is_trump(c)]
        return [c for c in cards if not self.is_trump(c) and c.suit == suit]

    def same(self, one: Card, two: Card) -> bool:
        return self.of(one) == self.of(two)

    def trump_type(self, cards: Cards) -> Trump:
        if len(cards) == 0 or len(cards) > 2:
            return Trump.NONE
        rank, suit, level = cards[0].rank, cards[0].suit, self.trump_rank
        if len(cards) == 1:
            return Trump.SINGLE if rank == level and suit != Suit.JOKER else Trump.NONE
        # Must be pairs
        if suit != cards[1].suit or rank != cards[1].rank:
            return Trump.NONE
        if suit == Suit.JOKER:
            return Trump.BIG_JOKER if rank == 2 else Trump.SMALL_JOKER
        if rank == level:
            return Trump.PAIR


class Player:
    def __init__(self, pid: int, name: str, sid: str) -> None:
        # Inputs
        self.pid = pid
        self.name = name
        self.sid = sid

        # Protected for testing
        self._hand: Cards = []

        # Public
        self.level = 2
        self.defender = False

    def json(self) -> dict:
        return {"pid": self.pid, "name": self.name, "level": self.level}

    def draw(self, cards: Cards) -> None:
        self._hand.extend(cards)

    # If non-empty cards is passed in, checks if the player has the specified cards.
    # If cards is empty, checks if the player has any cards in hand.
    def has_cards(self, cards: Cards | None = None) -> bool:
        if cards is None:
            return len(self._hand) > 0

        card_ids = set(card.id for card in cards)
        hand_ids = set(card.id for card in self._hand)

        # Cards are unique and all exist in hand
        return len(card_ids) == len(cards) and len(card_ids - hand_ids) == 0

    def cards_in_suit(self, order: Order, suit: Suit, include_trumps: bool) -> Cards:
        return order.cards_in_suit(self._hand, suit, include_trumps)

    # Always call has_cards before calling play
    def play(self, cards: Cards) -> None:
        card_ids = set(card.id for card in cards)
        self._hand = [card for card in self._hand if card.id not in card_ids]
