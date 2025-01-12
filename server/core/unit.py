from abc import ABC, abstractmethod
from itertools import chain
from typing import Self, TypeVar

from abstractions import Card, Cards, PlayerError, Room
from core import Order

TUnit = TypeVar("TUnit", bound="Unit")


class Unit(ABC):
    def __init__(self, cards: Cards) -> None:
        self._cards = cards
        self._highest = cards[0]
        self._length = len(cards)
        self._complement: Self | None = None
        self._name = type(self).__name__.lower()
        self._root = self._name

    @property
    def cards(self) -> Cards:
        return self._cards

    @property
    def highest(self) -> Card:
        return self._highest

    @property
    def length(self) -> int:
        return self._length

    @property
    def complement(self):
        return self._complement

    def _candidates(self, hand: list[TUnit], order: Order) -> list[Self]:
        candidates: list[Self] = []
        for unit in hand:
            candidates.extend(unit.decompose_into(self))
        candidates.sort(key=lambda s: order.of(s.highest))
        return candidates

    # Decompose this unit into units of the given type
    @abstractmethod
    def decompose_into[T: TUnit](self, unit: T) -> list[T]:
        raise NotImplementedError

    # Decompose this unit into smaller units of a lower class
    @abstractmethod
    def decompose(self) -> list[TUnit]:
        raise NotImplementedError

    # Generate card hints for a given set of candidates
    @abstractmethod
    def generate_hints(self, candidates: list[Self]) -> Cards:
        raise NotImplementedError

    # Default resolution implementation
    def _resolve(
        self, played: dict[int, Card], candidates: list[Self], room: Room
    ) -> list[int] | None:
        for candidate in candidates:
            ids = [card.id for card in candidate.cards]
            if all(id in played for id in ids):
                self._complement = candidate
                return ids

        raise PlayerError(
            f"Illegal format for {self._root}",
            f"There are available {self._name}s to play.",
            self.generate_hints(candidates),
        )

    def resolve(
        self, played: dict[int, Card], hand: list[TUnit], order: Order, room: Room
    ) -> list[int] | None:
        return self._resolve(played, self._candidates(hand, order), room)

    def reset(self) -> None:
        self._complement = None


class Single(Unit):
    def __init__(self, card: Card) -> None:
        super().__init__([card])

    def decompose_into(self, unit: Unit) -> list[Self]:
        return [self] if isinstance(unit, Single) else []

    # This should never be called
    def decompose(self) -> list[Unit]:
        raise RuntimeWarning(f"{self._name} cannot be decomposed.")

    def generate_hints(self, candidates: list[Self]) -> Cards:
        return [s.highest for s in candidates]


class Pair(Unit):
    def __init__(self, cards: Cards) -> None:
        super().__init__(cards)
        self.singles = [Single(card) for card in cards]
        self.peers: list[Self] = []

    def decompose_into(self, unit: Unit) -> list[Self]:
        if isinstance(unit, Pair):
            return [self]
        if isinstance(unit, Single):
            return self.singles
        return []

    def decompose(self) -> list[Unit]:
        return self.singles

    def generate_hints(self, candidates: list[Self]) -> Cards:
        return [card for pair in candidates for card in pair.cards]

    def resolve(
        self, played: dict[int, Card], hand: list[Unit], order: Order, room: Room
    ) -> list[int] | None:
        if len(candidates := self._candidates(hand, order)) > 0:
            return self._resolve(played, candidates, room)

    def reset(self) -> None:
        self._complement = None
        for single in self.singles:
            single.reset()


class Tractor(Unit):
    def __init__(self, pairs: list[Pair]) -> None:
        super().__init__([card for pair in pairs for card in pair.cards])
        self.pairs = pairs
        for pair in pairs:
            pair._root = self._name

    def decompose_into(self, unit: Unit) -> list[Self]:
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

    def decompose(self) -> list[Unit]:
        if len(self.pairs) == 2:
            return self.pairs
        return [Tractor(self.pairs[0:-1]), self.pairs[-1]]

    def generate_hints(self, candidates: list[Self]) -> Cards:
        ids = set()
        cards = [card for tractor in candidates for card in tractor.cards]
        return [ids.add(card.id) or card for card in cards if card.id not in ids]

    def __peers(self) -> list[Self]:
        peers = [self]
        for index, pair in enumerate(self.pairs):
            # There can only be one set of equivalent pairs in any suit:
            # non-trump suit trump rank pairs. We need to substitute the
            # pair. This implementation isn't robust and must be updated
            # if two or more equivalent pairs exist in a single Tractor.
            for peer in pair.peers:
                new_candidate = [p for p in self.pairs]
                new_candidate[index] = peer
                peers.append(Tractor(new_candidate))
        return peers

    def resolve(
        self, played: dict[int, Card], hand: list[Unit], order: Order, room: Room
    ) -> list[int] | None:
        candidates = list(chain(*[c.__peers() for c in self._candidates(hand, order)]))
        if len(candidates) > 0:
            return self._resolve(played, candidates, room)

    def reset(self) -> None:
        self._complement = None
        for pair in self.pairs:
            pair.reset()
