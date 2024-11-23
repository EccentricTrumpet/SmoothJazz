from itertools import batched
from random import shuffle
from typing import List
import unittest
from core.order import Order
from abstractions.types import Card
from abstractions.enums import Suit
from core.format import Format

# Jokers
BJ = "J2"
SJ = "J1"


# Utility to generate a list of cards
def initialize_cards(cards: List[str]) -> List[Card]:
    card_list = []
    for card in cards:
        card_list.append(Card(len(card_list), Suit(card[0]), int(card[1:])))
    return card_list


class FormatCreateTests(unittest.TestCase):

    def test_format_create_mixed_suits(self) -> None:
        order = Order(2)
        cards = initialize_cards([SJ, "S2", "S13"])
        shuffle(cards)
        format = Format(order, cards)

        self.assertTrue(format.is_toss)
        self.assertFalse(format.all_trumps)
        self.assertEqual(3, format.length)
        self.assertEqual(Suit.UNKNOWN, format.suit)
        self.assertEqual(0, len(format.tractors))
        self.assertEqual(0, len(format.pairs))
        self.assertEqual(0, len(format.singles))

    def test_format_create_single(self) -> None:
        order = Order(2)
        cases = [
            (SJ, Suit.JOKER, (True, Suit.JOKER)),
            (SJ, Suit.SPADE, (True, Suit.JOKER)),
            ("H2", Suit.JOKER, (True, Suit.HEART)),
            ("H3", Suit.HEART, (True, Suit.HEART)),
            ("H3", Suit.JOKER, (False, Suit.HEART)),
        ]

        for raw_card, trump_suit, expected in cases:
            with self.subTest(
                raw_card=raw_card, trump_suit=trump_suit, expected=expected
            ):
                cards = initialize_cards([raw_card])
                order.reset(trump_suit)
                format = Format(order, cards)
                (all_trumps, suit) = expected
                self.assertFalse(format.is_toss)
                self.assertEqual(all_trumps, format.all_trumps)
                self.assertEqual(suit, format.suit)
                self.assertEqual(1, format.length)
                self.assertEqual(0, len(format.tractors))
                self.assertEqual(0, len(format.pairs))
                self.assertEqual(1, len(format.singles))
                single = format.singles[0]
                self.assertEqual(cards[0].__str__(), single.cards[0].__str__())
                self.assertEqual(cards[0].__str__(), single.highest_card.__str__())

    def test_format_create_pair(self) -> None:
        order = Order(2)
        cases = [
            ([SJ, SJ], Suit.JOKER, (True, Suit.JOKER)),
            ([SJ, SJ], Suit.SPADE, (True, Suit.JOKER)),
            (["H2", "H2"], Suit.JOKER, (True, Suit.HEART)),
            (["H3", "H3"], Suit.HEART, (True, Suit.HEART)),
            (["H3", "H3"], Suit.JOKER, (False, Suit.HEART)),
        ]

        for raw_cards, trump_suit, expected in cases:
            with self.subTest(
                raw_cards=raw_cards, trump_suit=trump_suit, expected=expected
            ):
                cards = initialize_cards(raw_cards)
                order.reset(trump_suit)
                format = Format(order, cards)
                (all_trumps, suit) = expected
                self.assertFalse(format.is_toss)
                self.assertEqual(all_trumps, format.all_trumps)
                self.assertEqual(suit, format.suit)
                self.assertEqual(2, format.length)
                self.assertEqual(0, len(format.tractors))
                self.assertEqual(1, len(format.pairs))
                self.assertEqual(0, len(format.singles))
                pair = format.pairs[0]
                self.assertEqual(2, pair.length)
                self.assertTrue(cards[0].is_equivalent_to(cards[1]))
                self.assertTrue(cards[0].is_equivalent_to(pair.highest_card))
                self.assertTrue(cards[0].is_equivalent_to(pair.cards[0]))
                self.assertTrue(cards[0].is_equivalent_to(pair.cards[1]))

    def test_format_create_tractor(self) -> None:
        order = Order(2)
        cases = [
            # Big and small Jokers
            ([BJ, BJ, SJ, SJ], (2, Suit.JOKER), (True, Suit.JOKER)),
            ([BJ, BJ, SJ, SJ], (2, Suit.SPADE), (True, Suit.JOKER)),
            # Small Joker and trump suit trump rank pair
            ([SJ, SJ, "S2", "S2"], (2, Suit.SPADE), (True, Suit.UNKNOWN)),
            # Small Joker and trump rank pair, when no trump suit
            ([SJ, SJ, "S2", "S2"], (2, Suit.JOKER), (True, Suit.UNKNOWN)),
            # Non-trump rank pair and trump suit ace pair
            (["H2", "H2", "S1", "S1"], (2, Suit.SPADE), (True, Suit.UNKNOWN)),
            # Trump consecutive pairs
            (["S4", "S4", "S3", "S3"], (2, Suit.SPADE), (True, Suit.SPADE)),
            # Trump non-consecutive pairs, separated by trump rank
            (["S4", "S4", "S2", "S2"], (3, Suit.SPADE), (True, Suit.SPADE)),
            # Non-trump consecutive pairs
            (["S4", "S4", "S3", "S3"], (2, Suit.HEART), (False, Suit.SPADE)),
            # # Non-trump non-consecutive pairs, separated by trump rank
            (["S4", "S4", "S2", "S2"], (3, Suit.HEART), (False, Suit.SPADE)),
        ]

        for raw_cards, trump, expected in cases:
            with self.subTest(raw_cards=raw_cards, trump=trump, expected=expected):
                (trump_rank, trump_suit) = trump
                order = Order(trump_rank)
                order.reset(trump_suit)
                cards = initialize_cards(raw_cards)
                shuffle(cards)
                format = Format(order, cards)

                (all_trumps, suit) = expected
                self.assertFalse(format.is_toss)
                self.assertEqual(all_trumps, format.all_trumps)
                self.assertEqual(suit, format.suit)
                self.assertEqual(4, format.length)
                self.assertEqual(1, len(format.tractors))
                self.assertEqual(0, len(format.pairs))
                self.assertEqual(0, len(format.singles))

                cards.sort(key=lambda c: c.id)
                tractor = format.tractors[0]
                self.assertEqual(4, tractor.length)
                self.assertTrue(cards[0].is_equivalent_to(tractor.highest_card))
                self.assertTrue(cards[0].is_equivalent_to(tractor.cards[0]))
                for pair_cards, pair in zip(batched(cards, 2), tractor.pairs):
                    self.assertTrue(pair_cards[0].is_equivalent_to(pair_cards[1]))
                    self.assertTrue(pair_cards[0].is_equivalent_to(pair.cards[0]))
                    self.assertTrue(pair_cards[0].is_equivalent_to(pair.cards[1]))

    def test_format_create_toss_singles(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)

        cases = [
            # Trumps
            ([SJ, "S2", "S13"], (True, Suit.UNKNOWN)),
            # Non trumps
            (["H1", "H13", "H3"], (False, Suit.HEART)),
        ]

        for raw_cards, expected in cases:
            with self.subTest(raw_cards=raw_cards, expected=expected):
                cards = initialize_cards(raw_cards)
                shuffle(cards)
                format = Format(order, cards)
                (all_trumps, suit) = expected

                self.assertTrue(format.is_toss)
                self.assertEqual(all_trumps, format.all_trumps)
                self.assertEqual(suit, format.suit)
                self.assertEqual(3, format.length)
                self.assertEqual(0, len(format.tractors))
                self.assertEqual(0, len(format.pairs))
                self.assertEqual(3, len(format.singles))

                cards.sort(key=lambda c: c.id)
                for card, single in zip(cards, format.singles):
                    self.assertEqual(1, single.length)
                    self.assertEqual(card.__str__(), single.cards[0].__str__())
                    self.assertEqual(card.__str__(), single.highest_card.__str__())

    def test_format_create_toss_pairs(self) -> None:
        cases = [
            # Small Joker and non-trump suit trump rank pair
            ([SJ, SJ, "H2", "H2"], (2, Suit.SPADE), (True, Suit.UNKNOWN)),
            # 2 non-trump suit trump rank pairs
            (["C2", "C2", "H2", "H2"], (2, Suit.SPADE), (True, Suit.UNKNOWN)),
            # Trump consecutive pair, with one of trump rank
            (["S2", "S2", "S3", "S3"], (2, Suit.SPADE), (True, Suit.SPADE)),
            # Trump non-consecutive pair
            (["S2", "S2", "S4", "S4"], (2, Suit.SPADE), (True, Suit.SPADE)),
            # Non-trump non-consecutive pair
            (["H2", "H2", "H4", "H4"], (2, Suit.SPADE), (False, Suit.HEART)),
        ]

        for raw_cards, trump, expected in cases:
            with self.subTest(raw_cards=raw_cards, trump=trump, expected=expected):
                (trump_rank, trump_suit) = trump
                order = Order(trump_rank)
                order.reset(trump_suit)
                cards = initialize_cards(raw_cards)
                shuffle(cards)
                format = Format(order, cards)
                (all_trumps, suit) = expected

                self.assertTrue(format.is_toss)
                self.assertEqual(all_trumps, format.all_trumps)
                self.assertEqual(suit, format.suit)
                self.assertEqual(4, format.length)
                self.assertEqual(0, len(format.tractors))
                self.assertEqual(2, len(format.pairs))
                self.assertEqual(0, len(format.singles))

                cards.sort(key=lambda c: c.id)
                for pair_cards, pair in zip(batched(cards, 2), format.pairs):
                    self.assertEqual(
                        order.for_card(pair_cards[0]), order.for_card(pair.highest_card)
                    )

    def test_format_create_toss_combination(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)

        cases = [
            # Multiple tractors are sorted by length, then highest card
            (
                [
                    BJ,
                    BJ,
                    SJ,
                    SJ,
                    "H2",
                    "H2",
                    "S1",
                    "S1",
                    "S13",
                    "S13",
                    "S8",
                    "S8",
                    "S7",
                    "S7",
                ],
                (True, Suit.UNKNOWN, 3, 0, 0),
                [
                    (6, Card(0, Suit.HEART, 2)),
                    (4, Card(0, Suit.JOKER, 2)),
                    (4, Card(0, Suit.SPADE, 8)),
                ],
                [],
                [],
            ),
            # Trump suit trump rank pair, and 2 non-trump suit trump rank pairs, trump suit ace pair
            (
                ["S2", "S2", "H2", "H2", "C2", "C2", "S1", "S1"],
                (True, Suit.UNKNOWN, 1, 1, 0),
                [(6, Card(0, Suit.SPADE, 2))],
                [Card(0, Suit.HEART, 2)],
                [],
            ),
            # Combination of tractors, pairs and singles
            (
                [
                    SJ,
                    "H2",
                    "H2",
                    "S1",
                    "S13",
                    "S13",
                    "S11",
                    "S11",
                    "S10",
                    "S10",
                    "S8",
                    "S8",
                    "S7",
                    "S7",
                ],
                (True, Suit.UNKNOWN, 2, 2, 2),
                [
                    (4, Card(0, Suit.SPADE, 11)),
                    (4, Card(0, Suit.SPADE, 8)),
                ],
                [Card(0, Suit.HEART, 2), Card(0, Suit.SPADE, 13)],
                [Card(0, Suit.JOKER, 1), Card(0, Suit.SPADE, 1)],
            ),
        ]

        for (
            raw_cards,
            expected,
            expected_tractors,
            expected_pairs,
            expected_singles,
        ) in cases:
            with self.subTest(
                raw_cards=raw_cards,
                expected=expected,
                expected_tractors=expected_tractors,
                expected_pairs=expected_pairs,
                expected_singles=expected_singles,
            ):
                cards = initialize_cards(raw_cards)
                shuffle(cards)
                format = Format(order, cards)
                (all_trumps, suit, len_tractors, len_pairs, len_singles) = expected

                self.assertTrue(format.is_toss)
                self.assertEqual(all_trumps, format.all_trumps)
                self.assertEqual(suit, format.suit)
                self.assertEqual(len(cards), format.length)

                self.assertEqual(len_tractors, len(format.tractors))
                self.assertEqual(len_pairs, len(format.pairs))
                self.assertEqual(len_singles, len(format.singles))

                for (length, highest_card), tractor in zip(
                    expected_tractors, format.tractors
                ):
                    self.assertEqual(length, tractor.length)
                    self.assertTrue(highest_card.is_equivalent_to(tractor.highest_card))

                for highest_card, pair in zip(expected_pairs, format.pairs):
                    self.assertEqual(2, pair.length)
                    self.assertTrue(highest_card.is_equivalent_to(pair.highest_card))

                for highest_card, single in zip(expected_singles, format.singles):
                    self.assertEqual(1, single.length)
                    self.assertTrue(highest_card.is_equivalent_to(single.highest_card))


# Test that multiple trump suit trump rank and Non-trump Suit trump Rank tractors are all legal plays against a tractor
