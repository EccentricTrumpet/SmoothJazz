from unittest import TestCase
from itertools import batched, combinations
from random import shuffle
from typing import List, Sequence, Tuple
from abstractions import Card, Suit
from abstractions.responses import AlertResponse
from core.format import Format, FormatUnit, Single, Pair, Tractor
from core.order import Order
from testing import initialize, JB, JR
from testing.spades import S2, S3, S4, S5, S6, S7, S8, S9, SA, SJ, SK, ST
from testing.hearts import H2, H3, H4, H5, H6, H7, H8, HA, HK
from testing.diamonds import D2, D3, D4, D5, D6, D7, D8, D9


class FormatCreateTests(TestCase):

    def test_format_create_single(self) -> None:
        order = Order(2)
        cases = [
            ((JB, Suit.JOKER), (True, Suit.JOKER)),
            ((JB, Suit.SPADE), (True, Suit.JOKER)),
            ((H2, Suit.JOKER), (True, Suit.HEART)),
            ((H3, Suit.HEART), (True, Suit.HEART)),
            ((H3, Suit.JOKER), (False, Suit.HEART)),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (raw_card, trump_suit) = setup
                cards = initialize([raw_card])
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
                self.assertEqual(cards[0], single.cards[0])
                self.assertEqual(cards[0], single.highest)

    def test_format_create_pair(self) -> None:
        order = Order(2)
        cases = [
            (([JB, JB], Suit.JOKER), (True, Suit.JOKER)),
            (([JB, JB], Suit.SPADE), (True, Suit.JOKER)),
            (([H2, H2], Suit.JOKER), (True, Suit.HEART)),
            (([H3, H3], Suit.HEART), (True, Suit.HEART)),
            (([H3, H3], Suit.JOKER), (False, Suit.HEART)),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (raw_cards, trump_suit) = setup
                cards = initialize(raw_cards)
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
                self.assertTrue(cards[0].matches(cards[1]))
                self.assertTrue(cards[0].matches(pair.highest))
                self.assertTrue(cards[0].matches(pair.cards[0]))
                self.assertTrue(cards[0].matches(pair.cards[1]))

    def test_format_create_tractor(self) -> None:
        order = Order(2)
        cases = [
            # Big and small Jokers
            (([JR, JR, JB, JB], 2, Suit.JOKER), (True, Suit.JOKER)),
            (([JR, JR, JB, JB], 2, Suit.SPADE), (True, Suit.JOKER)),
            # Small Joker and trump suit trump rank pair
            (([JB, JB, S2, S2], 2, Suit.SPADE), (True, Suit.UNKNOWN)),
            # Small Joker and trump rank pair, when no trump suit
            (([JB, JB, S2, S2], 2, Suit.JOKER), (True, Suit.UNKNOWN)),
            # Non-trump rank pair and trump suit ace pair
            (([H2, H2, SA, SA], 2, Suit.SPADE), (True, Suit.UNKNOWN)),
            # Trump consecutive pairs
            (([S4, S4, S3, S3], 2, Suit.SPADE), (True, Suit.SPADE)),
            # Trump non-consecutive pairs, separated by trump rank
            (([S4, S4, S2, S2], 3, Suit.SPADE), (True, Suit.SPADE)),
            # Non-trump consecutive pairs
            (([S4, S4, S3, S3], 2, Suit.HEART), (False, Suit.SPADE)),
            # # Non-trump non-consecutive pairs, separated by trump rank
            (([S4, S4, S2, S2], 3, Suit.HEART), (False, Suit.SPADE)),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (raw_cards, trump_rank, trump_suit) = setup
                order = Order(trump_rank)
                order.reset(trump_suit)
                cards = initialize(raw_cards)
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
                self.assertTrue(cards[0].matches(tractor.highest))
                self.assertTrue(cards[0].matches(tractor.cards[0]))
                for pair_cards, pair in zip(batched(cards, 2), tractor.pairs):
                    self.assertTrue(pair_cards[0].matches(pair_cards[1]))
                    self.assertTrue(pair_cards[0].matches(pair.cards[0]))
                    self.assertTrue(pair_cards[0].matches(pair.cards[1]))

    def test_format_create_toss_singles(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)

        cases = [
            # Trumps
            ([JB, S2, SK], (True, Suit.UNKNOWN)),
            # Non trumps
            ([HA, HK, H3], (False, Suit.HEART)),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                cards = initialize(setup)
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
                    self.assertEqual(card, single.cards[0])
                    self.assertEqual(card, single.highest)

    def test_format_create_toss_pairs(self) -> None:
        cases = [
            # Small Joker and non-trump suit trump rank pair
            ([JB, JB, H2, H2], (True, Suit.UNKNOWN)),
            # 2 non-trump suit trump rank pairs
            ([D2, D2, H2, H2], (True, Suit.UNKNOWN)),
            # Trump consecutive pair, with one of trump rank
            ([S2, S2, S3, S3], (True, Suit.SPADE)),
            # Trump non-consecutive pair
            ([S2, S2, S4, S4], (True, Suit.SPADE)),
            # Non-trump non-consecutive pair
            ([H5, H5, H3, H3], (False, Suit.HEART)),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                order = Order(2)
                order.reset(Suit.SPADE)
                cards = initialize(setup)
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
                        order.for_card(pair_cards[0]), order.for_card(pair.highest)
                    )

    def test_format_create_toss_combination(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)
        empty: List[Card] = []

        cases = [
            # Multiple tractors are sorted by length, then highest card
            (
                [JR, JR, JB, JB, H2, H2, SA, SA, SK, SK, S8, S8, S7, S7],
                (
                    (True, Suit.UNKNOWN, 3, 0, 0),
                    [
                        (6, Card(0, Suit.HEART, 2)),
                        (4, Card(0, Suit.JOKER, 2)),
                        (4, Card(0, Suit.SPADE, 8)),
                    ],
                    empty,
                    empty,
                ),
            ),
            # Trump suit trump rank pair, and 2 non-trump suit trump rank pairs, trump suit ace pair
            (
                [S2, S2, H2, H2, "C2", "C2", SA, SA],
                (
                    (True, Suit.UNKNOWN, 1, 1, 0),
                    [(6, Card(0, Suit.SPADE, 2))],
                    [Card(0, Suit.HEART, 2)],
                    empty,
                ),
            ),
            # Combination of tractors, pairs and singles
            (
                [JB, H2, H2, SA, SK, SK, SJ, SJ, ST, ST, S8, S8, S7, S7],
                (
                    (True, Suit.UNKNOWN, 2, 2, 2),
                    [
                        (4, Card(0, Suit.SPADE, 11)),
                        (4, Card(0, Suit.SPADE, 8)),
                    ],
                    [Card(0, Suit.HEART, 2), Card(0, Suit.SPADE, 13)],
                    [Card(0, Suit.JOKER, 1), Card(0, Suit.SPADE, 1)],
                ),
            ),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                cards = initialize(setup)
                shuffle(cards)
                format = Format(order, cards)
                (
                    expected_format,
                    expected_tractors,
                    expected_pairs,
                    expected_singles,
                ) = expected
                (all_trumps, suit, len_tractors, len_pairs, len_singles) = (
                    expected_format
                )

                self.assertTrue(format.is_toss)
                self.assertEqual(all_trumps, format.all_trumps)
                self.assertEqual(suit, format.suit)
                self.assertEqual(len(cards), format.length)

                self.assertEqual(len_tractors, len(format.tractors))
                self.assertEqual(len_pairs, len(format.pairs))
                self.assertEqual(len_singles, len(format.singles))

                for (length, highest), tractor in zip(
                    expected_tractors, format.tractors
                ):
                    self.assertEqual(length, tractor.length)
                    self.assertTrue(highest.matches(tractor.highest))

                for highest, pair in zip(expected_pairs, format.pairs):
                    self.assertEqual(2, pair.length)
                    self.assertTrue(highest.matches(pair.highest))

                for highest, single in zip(expected_singles, format.singles):
                    self.assertEqual(1, single.length)
                    self.assertTrue(highest.matches(single.highest))


class FormatBeatTests(TestCase):
    def test_format_beat_length_mismatch(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)

        cases = [
            # Total length mismatch
            (([H3], [H3, H4]), False),
            # Tractors length mismatch
            (
                (
                    [H3, H3, H4, H4, H5, H5, H6, H6],
                    [D3, D3, D4, D4, D6, D6, D7, D7],
                ),
                False,
            ),
            # Pairs length mismatch
            (
                (
                    [H3, H3, H4, H4, H5, H5, H7, H7],
                    [D3, D3, D4, D4, D6, D6, D8, D8],
                ),
                False,
            ),
            # Singles length mismatch
            (
                (
                    [H3, H3, H4, H4, H5, H5, H6],
                    [D3, D3, D4, D4, D5, D6, D7],
                ),
                False,
            ),
            # Winning cases
            (
                (
                    [S3, S3, S4, S4, S5, S6, S6],
                    [S7, S7, S8, S8, S9, ST, ST],
                ),
                True,
            ),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (play1, play2) = tuple(map(initialize, setup))
                format1 = Format(order, play1)
                format2 = Format(order, play2)
                self.assertEqual(expected, format2.beats(format1))

    def test_format_beat_tractors(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)

        cases = [
            # Tractors length mismatch
            (
                (
                    [D3, D3, D4, D4, D5, D5, D7, D7, D8, D8, D9, D9],
                    [JR, JR, JB, JB, S2, S2, H2, H2, S9, S9, S8, S8],
                ),
                False,
            ),
            # Non-trump lost on high card
            (
                ([D5, D5, D6, D6], [D3, D3, D4, D4]),
                False,
            ),
            # Trump lost on high card
            (
                ([JR, JR, JB, JB], [S3, S3, S4, S4]),
                False,
            ),
            # Non-trump trumped
            (
                ([D5, D5, D6, D6], [S3, S3, S4, S4]),
                True,
            ),
            # Only highest tractor of a given length is considered
            (
                (
                    [JR, JR, JB, JB, S7, S7, S6, S6],
                    [S2, S2, H2, H2, S9, S9, S8, S8],
                ),
                False,
            ),
            (
                (
                    [S2, S2, H2, H2, S9, S9, S8, S8],
                    [JR, JR, JB, JB, S7, S7, S6, S6],
                ),
                True,
            ),
            # Tractors of different lengths considered
            (
                (
                    [JR, JR, JB, JB, S6, S6, S5, S5, S4, S4],
                    [S2, S2, H2, H2, S9, S9, S8, S8, S7, S7],
                ),
                False,
            ),
            (
                (
                    [S2, S2, H2, H2, S9, S9, S8, S8, S7, S7],
                    [JR, JR, JB, JB, S6, S6, S5, S5, S4, S4],
                ),
                False,
            ),
            (
                (
                    [S2, S2, H2, H2, S6, S6, S5, S5, S4, S4],
                    [JR, JR, JB, JB, S9, S9, S8, S8, S7, S7],
                ),
                True,
            ),
            # Winning cases
            (([S3, S3, S4, S4], [S2, S2, H2, H2]), True),
            (([H3, H3, H4, H4], [H7, H7, H8, H8]), True),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (play1, play2) = tuple(map(initialize, setup))
                format1 = Format(order, play1)
                format2 = Format(order, play2)
                self.assertEqual(expected, format2.beats(format1))

    def test_format_beat_pairs(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)

        cases = [
            # Non-trump lost on high card
            (([D5, D5], [D3, D3]), False),
            # Trump lost on high card
            (([JR, JR], [S3, S3]), False),
            # Non-trump trumped
            (([D5, D5], [S3, S3]), True),
            # Only highest pair is considered
            (([JR, JR, S7, S7], [JB, JB, S9, S9]), False),
            (([JB, JB, S9, S9], [JR, JR, S7, S7]), True),
            # Winning cases
            (([S3, S3], [S2, S2]), True),
            (([H3, H3], [H7, H7]), True),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (play1, play2) = tuple(map(initialize, setup))
                format1 = Format(order, play1)
                format2 = Format(order, play2)
                self.assertEqual(expected, format2.beats(format1))

    def test_format_beat_singles(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)

        cases = [
            # Non-trump lost on high card
            (([D5], [D3]), False),
            # Trump lost on high card
            (([JR], [S3]), False),
            # Non-trump trumped
            (([D5], [S3]), True),
            # Only highest single is considered
            (([JR, S7], [JB, S9]), False),
            (([JB, S9], [JR, S7]), True),
            # Equivalent card loses
            (([D5], [D5]), False),
            (([S2], [S2]), False),
            # Winning cases
            (([S3], [S2]), True),
            (([H3], [H7]), True),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (play1, play2) = tuple(map(initialize, setup))
                format1 = Format(order, play1)
                format2 = Format(order, play2)
                self.assertEqual(expected, format2.beats(format1))


class FormatUnitTests(TestCase):
    def test_format_unit_single_decompose_into(self) -> None:
        [S3Card, S4Card, S5Card] = initialize([S3, S4, S5])
        unit = Single(S3Card)

        cases: Sequence[Tuple[FormatUnit, Sequence[FormatUnit]]] = [
            # Single
            (Single(S4Card), [Single(S3Card)]),
            # Pair
            (Pair([Single(S4Card), Single(S4Card)]), []),
            # Tractor
            (
                Tractor(
                    [
                        Pair([Single(S4Card), Single(S4Card)]),
                        Pair([Single(S5Card), Single(S5Card)]),
                    ]
                ),
                [],
            ),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                actual = unit.decompose_into(setup)
                self.assertEqual(len(expected), len(actual))
                for expected_unit, actual_unit in zip(expected, actual):
                    self.assertEqual(expected_unit.highest, actual_unit.highest)

    def test_format_unit_pair_decompose_into(self) -> None:
        [S3Card, S4Card, S5Card] = initialize([S3, S4, S5])
        unit = Pair([Single(S3Card), Single(S3Card)])

        cases: Sequence[Tuple[FormatUnit, Sequence[FormatUnit]]] = [
            # Single
            (Single(S4Card), [Single(S3Card), Single(S3Card)]),
            # Pair
            (
                Pair([Single(S4Card), Single(S4Card)]),
                [Pair([Single(S3Card), Single(S3Card)])],
            ),
            # Tractor
            (
                Tractor(
                    [
                        Pair([Single(S4Card), Single(S4Card)]),
                        Pair([Single(S5Card), Single(S5Card)]),
                    ]
                ),
                [],
            ),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                actual = unit.decompose_into(setup)
                self.assertEqual(len(expected), len(actual))
                for expected_unit, actual_unit in zip(expected, actual):
                    self.assertEqual(expected_unit.highest, actual_unit.highest)

    def test_format_unit_tractor_decompose_into(self) -> None:
        [S3Card, S4Card, S5Card, S6Card, S7Card] = initialize([S3, S4, S5, S6, S7])
        unit = Tractor(
            [
                Pair([Single(S5Card), Single(S5Card)]),
                Pair([Single(S6Card), Single(S6Card)]),
                Pair([Single(S7Card), Single(S7Card)]),
            ]
        )

        cases: Sequence[Tuple[FormatUnit, Sequence[FormatUnit]]] = [
            # Single
            (
                Single(S4Card),
                [
                    Single(S5Card),
                    Single(S5Card),
                    Single(S6Card),
                    Single(S6Card),
                    Single(S7Card),
                    Single(S7Card),
                ],
            ),
            # Pair
            (
                Pair([Single(S4Card), Single(S4Card)]),
                [
                    Pair([Single(S5Card), Single(S5Card)]),
                    Pair([Single(S6Card), Single(S6Card)]),
                    Pair([Single(S7Card), Single(S7Card)]),
                ],
            ),
            # Tractor
            (
                Tractor(
                    [
                        Pair([Single(S3Card), Single(S3Card)]),
                        Pair([Single(S4Card), Single(S4Card)]),
                    ]
                ),
                [
                    Tractor(
                        [
                            Pair([Single(S5Card), Single(S5Card)]),
                            Pair([Single(S6Card), Single(S6Card)]),
                        ]
                    ),
                    Tractor(
                        [
                            Pair([Single(S6Card), Single(S6Card)]),
                            Pair([Single(S7Card), Single(S7Card)]),
                        ]
                    ),
                ],
            ),
        ]

        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                actual = unit.decompose_into(setup)
                self.assertEqual(len(expected), len(actual))
                for expected_unit, actual_unit in zip(expected, actual):
                    self.assertEqual(expected_unit.highest, actual_unit.highest)


class FormatResolvePlayTests(TestCase):
    def test_format_try_play_single_with_complement(self) -> None:
        order = Order(2)
        lead = Format(order, initialize([S3]))
        hand = initialize([S4, S5, S5, S7, S7, S8, S8])

        # Any of the cards in hand can be played
        for card in hand:
            self.assertIsNone(lead.resolve_play([card], hand))
            self.assertEqual(1, len(lead.units))
            single = lead.units[0]
            self.assertIsInstance(single.complement, Single)
            self.assertListEqual([card], single.complement.cards)

    def test_format_try_play_pair_with_complement(self) -> None:
        order = Order(2)
        lead = Format(order, initialize([S3, S3]))
        hand = initialize([S8, S8, S7, S7, S5, S5, S4])

        # Only pairs and tractor pairs can be played
        cases = [
            # Tractor Pair
            [0, 1],
            [2, 3],
            # Pair
            [4, 5],
        ]

        for setup in cases:
            with self.subTest(setup=setup):
                play = [hand[i] for i in setup]

                self.assertIsNone(lead.resolve_play(play, hand))
                self.assertEqual(1, len(lead.units))
                pair = lead.units[0]
                self.assertIsInstance(pair.complement, Pair)
                self.assertListEqual(play, pair.complement.cards)

    def test_format_try_play_pair_no_complement(self) -> None:
        order = Order(2)
        lead = Format(order, initialize([S3, S3]))
        hand = initialize([S8, S7, S5, S4])

        for play in combinations(hand, 2):
            self.assertIsNone(lead.resolve_play(play, hand))
            self.assertEqual(1, len(lead.units))
            pair = lead.units[0]
            self.assertIsNone(pair.complement)

    def test_format_try_play_pair_invalid(self) -> None:
        order = Order(2)
        lead = Format(order, initialize([S3, S3]))
        hand = initialize([S8, S8, S7, S7, S5, S5, S4])

        cases = [
            [1, 2],
            [3, 4],
            [5, 6],
        ]

        for setup in cases:
            with self.subTest(setup=setup):
                play = [hand[i] for i in setup]

                alert = lead.resolve_play(play, hand)
                self.assertIsInstance(alert, AlertResponse)
                self.assertEqual("Illegal format for pair", alert._title)
                self.assertEqual("There are available pairs to play.", alert._message)
                self.assertListEqual(hand[0:-1], alert._hint_cards)

    def test_format_try_play_tractor_with_complement(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)
        lead = Format(order, initialize([S3, S3, S4, S4]))
        hand = initialize(
            [S2, S2, H2, H2, D2, D2, SJ, SJ, ST, ST, S8, S8, S7, S7, S6, S6]
        )

        # Only tractor can be played
        cases = [
            # Matching Tractor
            [6, 7, 8, 9],
            # Equivalent Tractor
            [0, 1, 2, 3],
            [0, 1, 4, 5],
            # Decomposed Tractor
            [10, 11, 12, 13],
            [12, 13, 14, 15],
        ]

        for setup in cases:
            with self.subTest(setup=setup):
                play = [hand[i] for i in setup]

                self.assertIsNone(lead.resolve_play(play, hand))
                self.assertEqual(1, len(lead.units))
                tractor = lead.units[0]
                self.assertIsInstance(tractor.complement, Tractor)
                self.assertEqual(play[0], tractor.complement.highest)
                self.assertListEqual(play, tractor.complement.cards)

    def test_format_try_play_tractor_no_complement(self) -> None:
        order = Order(2)
        lead = Format(order, initialize([S3, S3, S4, S4]))

        cases = [
            ([S7, S7, S6, S5, S5, S4], [0, 1, 3, 4]),
            ([S8, S7, S7, S6, S5, S4], [0, 1, 2, 3]),
            ([S8, S7, S7, S6, S5, S4], [1, 2, 3, 4]),
        ]

        for setup in cases:
            with self.subTest(setup=setup):
                (hand, play) = setup
                hand = initialize(hand)
                play = [hand[i] for i in play]

                self.assertIsNone(lead.resolve_play(play, hand))
                self.assertEqual(1, len(lead.units))
                tractor = lead.units[0]
                self.assertIsNone(tractor.complement)

    def test_format_try_play_tractor_invalid(self) -> None:
        order = Order(2)
        cases = [
            (
                (
                    [S3, S3, S4, S4, S5, S5],
                    [ST, ST, S8, S8, S7, S7, S4, S4],
                    [0, 1, 2, 3, 6, 7],
                ),
                ("There are available tractors to play.", [2, 3, 4, 5]),
            ),
            (
                ([S3, S3, S4, S4], [S8, S8, S7, S7, S5, S5, S4], [2, 3, 4, 5]),
                ("There are available tractors to play.", [0, 1, 2, 3]),
            ),
            (
                ([S3, S3, S4, S4], [S7, S7, S6, S5, S5, S4], [2, 3, 4, 5]),
                ("There are available pairs to play.", [0, 1]),
            ),
            (
                ([S3, S3, S4, S4], [S7, S7, S6, S5, S5, S4], [0, 1, 2, 3]),
                ("There are available pairs to play.", [3, 4]),
            ),
            (
                ([S3, S3, S4, S4], [S7, S7, S6, S5, S5, S4], [0, 2, 3, 5]),
                ("There are available pairs to play.", [0, 1, 3, 4]),
            ),
            (
                ([S3, S3, S4, S4], [S8, S7, S7, S6, S5, S4], [2, 3, 4, 5]),
                ("There are available pairs to play.", [1, 2]),
            ),
        ]

        for case in cases:
            (setup, expected) = case
            with self.subTest(setup=setup, expected=expected):
                (lead, hand, play) = setup
                lead = Format(order, initialize(lead))
                hand = initialize(hand)
                play = [hand[i] for i in play]
                (message, hint) = expected
                hint = [hand[i] for i in hint]

                alert = lead.resolve_play(play, hand)
                self.assertIsInstance(alert, AlertResponse)
                self.assertEqual("Illegal format for tractor", alert._title)
                self.assertEqual(message, alert._message)
                self.assertListEqual(hint, alert._hint_cards)
