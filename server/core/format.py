import logging
from typing import Sequence, Set, Tuple, TypeVar
from abstractions.enums import Suit
from abstractions.types import Card
from core.order import Order


TFormat = TypeVar("TFormat", bound="Format")
TSingle = TypeVar("TFormat", bound="Single")
TPair = TypeVar("TFormat", bound="Pair")
TTractor = TypeVar("TFormat", bound="Tractor")


class Single:
    def __init__(self, card: Card) -> None:
        self.cards: Sequence[Card] = [card]
        self.highest_card = card
        self.matched = False
        self.complement: TSingle | None = None

    @property
    def length(self) -> int:
        return len(self.cards)

    def reset(self) -> None:
        self.matched = False
        self.complement = None


class Pair:
    def __init__(self, cards: Sequence[Card]) -> None:
        self.cards: Sequence[Card] = cards
        self.highest_card = cards[0]
        self.matched = False
        self.complement: TPair | None = None

    @property
    def length(self) -> int:
        return len(self.cards)

    def reset(self) -> None:
        self.matched = False
        self.complement = None


class Tractor:
    def __init__(self, pairs: Sequence[Pair]) -> None:
        self.cards: Sequence[Card] = [card for pair in pairs for card in pair.cards]
        self.pairs = pairs
        # Assume cards are sorted in increasing order
        self.highest_card = self.cards[0]
        self.matched = False
        self.complement: TTractor | None = None

    @property
    def length(self) -> int:
        return len(self.cards)

    def reset(self) -> None:
        self.matched = False
        self.complement = None


# Container class for format of set of cards in a play
# Assume non-zero number of cards
class Format:
    def __init__(
        self,
        order: Order,
        cards: Sequence[Card],
    ) -> None:
        self.__order = order
        self.__cards = cards

        self.all_trumps = True
        all_non_trumps = True
        suits: Set[Suit] = set()

        for card in cards:
            suits.add(card.suit)
            is_trump = order.is_trump(card)
            self.all_trumps = self.all_trumps and is_trump
            all_non_trumps = all_non_trumps and not is_trump

        self.suit = (
            Suit.UNKNOWN
            if len(suits) > 1 or self.all_trumps == all_non_trumps
            else next(iter(suits))
        )
        self.suited = self.all_trumps or (all_non_trumps and self.suit != Suit.UNKNOWN)
        (self.singles, self.pairs, self.tractors) = (
            self.__create(cards) if self.suited else ([], [], [])
        )
        self.is_toss = len(self.tractors) + len(self.pairs) + len(self.singles) != 1

    def __create(
        self, cards: Sequence[Card]
    ) -> Tuple[Sequence[Single], Sequence[Pair], Sequence[Tractor]]:
        sorted_cards = sorted(
            cards, key=lambda card: (self.__order.for_card(card), card.suit)
        )
        singles: Sequence[Single] = []
        pairs: Sequence[Pair] = []
        tractors: Sequence[Tractor] = []

        # Resolve singles and pairs
        i = 0
        while i < len(sorted_cards):
            if i < len(sorted_cards) - 1 and sorted_cards[i].is_equivalent_to(
                sorted_cards[i + 1]
            ):
                pairs.append(Pair([sorted_cards[i], sorted_cards[i + 1]]))
                i += 2
            else:
                singles.append(Single(sorted_cards[i]))
                i += 1

        # Resolve tractors
        i = 0
        orphan_pairs: Sequence[Pair] = []
        deduped_pairs: Sequence[Pair] = []
        last_card_order = -1

        # Separate duplicate non-trump pairs when resolving tractors
        for pair in pairs:
            pair_order = self.__order.for_card(pair.highest_card)
            if pair_order == last_card_order:
                orphan_pairs.append(pair)
            else:
                last_card_order = pair_order
                deduped_pairs.append(pair)

        # Resolve tractors using deduped pairs
        pairs_len = len(deduped_pairs)
        while i < pairs_len:
            j = i
            tractor_pairs = [deduped_pairs[j]]
            while (
                j < pairs_len - 1
                and self.__order.for_card(deduped_pairs[j + 1].highest_card)
                - self.__order.for_card(deduped_pairs[j].highest_card)
                == 1
            ):
                tractor_pairs.append(deduped_pairs[j + 1])
                j += 1
            if j != i:
                tractors.append(Tractor(tractor_pairs))
                i = j + 1
            else:
                orphan_pairs.append(deduped_pairs[i])
                i += 1

        tractors.sort(key=lambda t: (-t.length, self.__order.for_card(t.highest_card)))
        orphan_pairs.sort(key=lambda p: self.__order.for_card(p.highest_card))

        return (singles, orphan_pairs, tractors)

    @property
    def length(self) -> int:
        return len(self.__cards)

    def reset(self) -> None:
        for tractor in self.tractors:
            tractor.reset()
        for pair in self.pairs:
            pair.reset()
        for single in self.singles:
            single.reset()

    def reform_with(self, format: TFormat):
        self.tractors = [tractor.complement for tractor in format.tractors]
        self.pairs = [pair.complement for pair in format.pairs]
        self.singles = [single.complement for single in format.singles]

    def cards_in_suit(self, suit: Suit, include_trumps: bool) -> Sequence[Card]:
        return [
            card
            for card in self.__cards
            if (include_trumps and self.__order.is_trump(card))
            or (
                not include_trumps
                and not self.__order.is_trump(card)
                and card.suit == suit
            )
        ]
