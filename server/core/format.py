from itertools import chain
from typing import Self, Sequence, Tuple

from abstractions import Card, Room, Suit
from core import Order
from core.unit import Pair, Single, Tractor


# Container class for format of set of cards in a play
# Assume non-zero number of cards
class Format:
    def __init__(self, order: Order, cards: Sequence[Card]) -> None:
        self.__order = order
        self.__cards = cards

        self.trumps = all(order.is_trump(card) for card in cards)
        no_trumps = all(not order.is_trump(card) for card in cards)
        suits = set([card.suit for card in cards])
        self.suit = (
            Suit.UNKNOWN
            if len(suits) > 1 or self.trumps == no_trumps
            else next(iter(suits))
        )
        self.suited = self.trumps or (no_trumps and self.suit != Suit.UNKNOWN)

        self.singles: Sequence[Single]
        self.pairs: Sequence[Pair]
        self.tractors: Sequence[Tractor]
        self.singles, self.pairs, self.tractors = (
            self.__create(cards) if self.suited else ([], [], [])
        )
        self.units = list(chain(self.tractors, self.pairs, self.singles))
        self.is_toss = len(self.tractors) + len(self.pairs) + len(self.singles) != 1

    def __create(
        self, cards: Sequence[Card]
    ) -> Tuple[Sequence[Single], Sequence[Pair], Sequence[Tractor]]:
        order = self.__order
        cards = sorted(cards, key=lambda card: (order.of(card), card.suit))
        singles: Sequence[Single] = []
        pairs: Sequence[Pair] = []
        tractors: Sequence[Tractor] = []

        # Resolve singles and pairs
        i = 0
        while i < len(cards):
            if i < len(cards) - 1 and cards[i].matches(cards[i + 1]):
                pairs.append(Pair([cards[i], cards[i + 1]]))
                i += 2
            else:
                singles.append(Single(cards[i]))
                i += 1

        # Resolve tractors
        i = 0
        all: Sequence[Pair] = []
        unique: Sequence[Pair] = []

        # Separate duplicate non-trump pairs when resolving tractors
        for pair in pairs:
            if unique and order.same(unique[-1].highest, pair.highest):
                all.append(pair)
                unique[-1].peers.append(pair)
            else:
                unique.append(pair)

        # Resolve tractors using deduped pairs
        pairs_len = len(unique)
        while i < pairs_len:
            j = i
            tractor_pairs = [unique[j]]
            while (
                j < pairs_len - 1
                and order.of(unique[j + 1].highest) - order.of(unique[j].highest) == 1
            ):
                tractor_pairs.append(unique[j + 1])
                j += 1
            if j != i:
                tractors.append(Tractor(tractor_pairs))
                i = j + 1
            else:
                all.append(unique[i])
                i += 1

        tractors.sort(key=lambda t: (-t.length, order.of(t.highest)))
        all.sort(key=lambda p: order.of(p.highest))

        return (singles, all, tractors)

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

    def reform(self, format: Self) -> None:
        if all(unit.complement is not None for unit in format.units):
            self.tractors = [tractor.complement for tractor in format.tractors]
            self.pairs = [pair.complement for pair in format.pairs]
            self.singles = [single.complement for single in format.singles]
            self.units = list(chain(self.tractors, self.pairs, self.singles))

    def cards_in_suit(self, suit: Suit, include_trumps: bool) -> Sequence[Card]:
        return self.__order.cards_in_suit(self.__cards, suit, include_trumps)

    def play(
        self, played_cards: Sequence[Card], hand_cards: Sequence[Card], room: Room
    ) -> None:
        played_dict = {card.id: card for card in played_cards}
        hand_dict = {card.id: card for card in hand_cards}
        stack = [unit for unit in reversed(self.units)]

        while stack:
            unit = stack.pop()
            hand_format = Format(self.__order, hand_dict.values())
            result = unit.resolve(played_dict, hand_format.units, self.__order, room)
            if result is None:
                stack.extend(reversed(unit.decompose()))
                continue
            for id in result:
                del played_dict[id]
                del hand_dict[id]

    def beats(self, other: Self) -> bool:
        # This check will be obsolete once format matching is completed
        # For now this is a quick sanity check for prototyping
        if (
            self.length != other.length
            or len(self.tractors) != len(other.tractors)
            or len(self.pairs) != len(other.pairs)
            or len(self.singles) != len(other.singles)
        ):
            print("Format comparison lost: length mismatch")
            return False

        order = self.__order
        tractor_length = 0

        for tractor, other_tractor in zip(self.tractors, other.tractors):
            if tractor.length != other_tractor.length:
                print("Format comparison lost: tractor length mismatch")
                return False
            if tractor.length != tractor_length:
                tractor_length = tractor.length
                # Highest tractor of a given length, compare highest cards
                if order.of(tractor.highest) >= order.of(other_tractor.highest):
                    print("Format comparison lost: tractor order")
                    return False

        if len(self.pairs) > 0 and order.of(self.pairs[0].highest) >= order.of(
            other.pairs[0].highest
        ):
            print("Format comparison lost: pair order")
            return False

        if len(self.singles) > 0 and order.of(self.singles[0].highest) >= order.of(
            other.singles[0].highest
        ):
            print("Format comparison lost: single order")
            return False

        return True
