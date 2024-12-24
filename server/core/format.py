from abc import ABC, abstractmethod
from itertools import chain
from typing import Dict, List, Self, Sequence, Set, Tuple, TypeVar
from abstractions import Suit, Card
from abstractions.responses import AlertResponse
from core.order import Order


TFormatUnit = TypeVar("TFormatUnit", bound="FormatUnit")
TFormat = TypeVar("TFormat", bound="Format")


class FormatUnit(ABC):
    def __init__(self, cards: Sequence[Card]) -> None:
        self._cards = cards
        self._highest = cards[0]
        self._length = len(cards)
        self._complement: Self | None = None
        self._name = type(self).__name__.lower()
        self.root_name = self._name

    @property
    def cards(self):
        return self._cards

    @property
    def highest(self):
        return self._highest

    @property
    def length(self):
        return self._length

    @property
    def complement(self):
        return self._complement

    @complement.setter
    def complement(self, complement: Self):
        self._complement = complement

    @property
    def _root_name(self):
        return self.__root_name

    @_root_name.setter
    def root_name(self, name: str):
        self.__root_name = name

    def reset(self):
        self._complement = None

    @abstractmethod
    def decompose_into(self, unit: TFormatUnit) -> Sequence[TFormatUnit]:
        pass

    @abstractmethod
    def decompose_into(self, unit: TFormatUnit) -> Sequence[TFormatUnit]:
        pass

    def resolve(
        self, played: Dict[int, Card], hand: TFormat, order: Order
    ) -> Sequence[int] | AlertResponse | None:
        pass


class Single(FormatUnit):
    def __init__(self, card: Card) -> None:
        super().__init__([card])

    def decompose_into(self, unit: FormatUnit) -> Sequence[Self]:
        if isinstance(unit, Single):
            return [self]
        return []

    # This should never be called
    def decompose(self) -> Sequence[FormatUnit]:
        return []

    def resolve(
        self, played: Dict[int, Card], hand: TFormat, order: Order
    ) -> Sequence[int] | AlertResponse | None:
        candidates: Sequence[Single] = []
        for unit in hand.units:
            candidates.extend(unit.decompose_into(self))
        candidates.sort(key=lambda s: order.for_card(s.highest))

        for candidate in candidates:
            ids = [card.id for card in candidate.cards]
            if all(id in played for id in ids):
                self.complement = candidate
                return ids

        # This should be impossible, but as a failsafe:
        return AlertResponse(
            "",
            f"Illegal format for {self._root_name}",
            f"There are available {self._name}s to play.",
            [s.highest for s in candidates],
        )


class Pair(FormatUnit):
    def __init__(self, singles: Sequence[Single]) -> None:
        super().__init__([card for single in singles for card in single.cards])
        self.singles = singles
        self.peer_pairs: List[Self] = []

    def decompose_into(self, unit: FormatUnit) -> Sequence[Self]:
        if isinstance(unit, Pair):
            return [self]
        if isinstance(unit, Single):
            return self.singles
        return []

    def decompose(self) -> Sequence[FormatUnit]:
        return self.singles

    def resolve(
        self, played: Dict[int, Card], hand: TFormat, order: Order
    ) -> Sequence[int] | AlertResponse | None:
        candidates: Sequence[Pair] = []
        for unit in hand.units:
            candidates.extend(unit.decompose_into(self))
        candidates.sort(key=lambda s: order.for_card(s.highest))

        # Return None so unit will be decomposed before resolving again
        if not candidates:
            return None

        for candidate in candidates:
            ids = [card.id for card in candidate.cards]
            if all(id in played for id in ids):
                self.complement = candidate
                return ids

        return AlertResponse(
            "",
            f"Illegal format for {self._root_name}",
            f"There are available {self._name}s to play.",
            [card for pair in candidates for card in pair.cards],
        )

    def reset(self):
        self._complement = None
        for single in self.singles:
            single.reset()


class Tractor(FormatUnit):
    def __init__(self, pairs: Sequence[Pair]) -> None:
        super().__init__([card for pair in pairs for card in pair.cards])
        self.pairs = pairs
        for pair in pairs:
            pair.root_name = self._name

    def decompose_into(self, unit: FormatUnit) -> Sequence[Self]:
        if isinstance(unit, Tractor) and self.length >= unit.length:
            return [
                Tractor(self.pairs[i : i + len(unit.pairs)])
                for i in range(len(self.pairs) - len(unit.pairs) + 1)
            ]
        if isinstance(unit, Pair):
            return self.pairs
        if isinstance(unit, Single):
            return [Single(card) for card in self.cards]
        return []

    def decompose(self) -> Sequence[FormatUnit]:
        if len(self.pairs) == 2:
            return self.pairs
        return [Tractor(self.pairs[0:-1]), self.pairs[-1]]

    def reset(self):
        self._complement = None
        for pair in self.pairs:
            pair.reset()

    def resolve_full_candidates(self) -> Sequence[Self]:
        candidates = [self]
        for index, pair in enumerate(self.pairs):
            # There can only be one set of equivalent pairs in any suit:
            # non-trump suit trump ranks. We need to substitute the pair.
            for peer in pair.peer_pairs:
                new_candidate = [p for p in self.pairs]
                new_candidate[index] = peer
                candidates.append(Tractor(new_candidate))
        return candidates

    def resolve(
        self, played: Dict[int, Card], hand: TFormat, order: Order
    ) -> Sequence[int] | AlertResponse | None:
        candidates: Sequence[Self] = []
        for unit in hand.units:
            candidates.extend(unit.decompose_into(self))
        candidates.sort(key=lambda s: order.for_card(s.highest))

        full_candidates = []
        for candidate in candidates:
            full_candidates.extend(candidate.resolve_full_candidates())
        candidates = full_candidates

        # Return None so unit will be decomposed before resolving again
        if not candidates:
            return None

        for candidate in candidates:
            ids = [card.id for card in candidate.cards]
            if all(id in played for id in ids):
                self.complement = candidate
                return ids

        card_ids = set()
        unique_cards = []
        for tractor in candidates:
            for card in tractor.cards:
                if card.id not in card_ids:
                    unique_cards.append(card)
                    card_ids.add(card.id)

        return AlertResponse(
            "",
            f"Illegal format for {self._root_name}",
            f"There are available {self._name}s to play.",
            unique_cards,
        )


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
        self.units: Sequence[FormatUnit] = list(
            chain(self.tractors, self.pairs, self.singles)
        )
        self.is_toss = len(self.tractors) + len(self.pairs) + len(self.singles) != 1

    def __create(
        self, cards: Sequence[Card]
    ) -> Tuple[List[Single], List[Pair], List[Tractor]]:
        sorted_cards = sorted(
            cards, key=lambda card: (self.__order.for_card(card), card.suit)
        )
        singles: List[Single] = []
        pairs: List[Pair] = []
        tractors: List[Tractor] = []

        # Resolve singles and pairs
        i = 0
        while i < len(sorted_cards):
            if i < len(sorted_cards) - 1 and sorted_cards[i].matches(
                sorted_cards[i + 1]
            ):
                pairs.append(
                    Pair([Single(sorted_cards[i]), Single(sorted_cards[i + 1])])
                )
                i += 2
            else:
                singles.append(Single(sorted_cards[i]))
                i += 1

        # Resolve tractors
        i = 0
        all_pairs: List[Pair] = []
        unique_pairs: List[Pair] = []

        # Separate duplicate non-trump pairs when resolving tractors
        for pair in pairs:
            if unique_pairs and (
                self.__order.for_card(unique_pairs[-1].highest)
                == self.__order.for_card(pair.highest)
            ):
                all_pairs.append(pair)
                unique_pairs[-1].peer_pairs.append(pair)
            else:
                unique_pairs.append(pair)

        # Resolve tractors using deduped pairs
        pairs_len = len(unique_pairs)
        while i < pairs_len:
            j = i
            tractor_pairs = [unique_pairs[j]]
            while (
                j < pairs_len - 1
                and self.__order.for_card(unique_pairs[j + 1].highest)
                - self.__order.for_card(unique_pairs[j].highest)
                == 1
            ):
                tractor_pairs.append(unique_pairs[j + 1])
                j += 1
            if j != i:
                tractors.append(Tractor(tractor_pairs))
                i = j + 1
            else:
                all_pairs.append(unique_pairs[i])
                i += 1

        tractors.sort(key=lambda t: (-t.length, self.__order.for_card(t.highest)))
        all_pairs.sort(key=lambda p: self.__order.for_card(p.highest))

        return (singles, all_pairs, tractors)

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

    def try_reform(self, format: Self) -> bool:
        can_reform = all(unit.complement is not None for unit in format.units)
        if not can_reform:
            return False
        self.tractors = [tractor.complement for tractor in format.tractors]
        self.pairs = [pair.complement for pair in format.pairs]
        self.singles = [single.complement for single in format.singles]
        self.units = list(chain(self.tractors, self.pairs, self.singles))

    def cards_in_suit(self, suit: Suit, include_trumps: bool) -> Sequence[Card]:
        return self.__order.cards_in_suit(self.__cards, suit, include_trumps)

    def resolve_play(
        self, played_cards: Sequence[Card], hand_cards: Sequence[Card]
    ) -> AlertResponse | None:
        played_dict = {card.id: card for card in played_cards}
        hand_dict = {card.id: card for card in hand_cards}
        stack = [unit for unit in reversed(self.units)]

        while stack:
            unit = stack.pop()
            hand_format = Format(self.__order, hand_dict.values())
            result = unit.resolve(played_dict, hand_format, self.__order)
            if isinstance(result, AlertResponse):
                return result
            if result is None:
                stack.extend(reversed(unit.decompose()))
                continue
            for id in result:
                del played_dict[id]
                del hand_dict[id]

        return None

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
                if order.for_card(tractor.highest) >= order.for_card(
                    other_tractor.highest
                ):
                    print("Format comparison lost: tractor order")
                    return False

        if len(self.pairs) > 0 and order.for_card(
            self.pairs[0].highest
        ) >= order.for_card(other.pairs[0].highest):
            print("Format comparison lost: pair order")
            return False

        if len(self.singles) > 0 and order.for_card(
            self.singles[0].highest
        ) >= order.for_card(other.singles[0].highest):
            print("Format comparison lost: single order")
            return False

        return True
