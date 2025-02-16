from unittest import TestCase

from abstractions import Card, Cards, PlayerError, Suit
from core import Order, Player
from core.trick import Trick
from testing import JB, initialize
from testing.diamonds import D3, D4
from testing.hearts import H3, H4, H5, H6, H7
from testing.spades import S2, S3, S4, S5, S6, S7, S8, S9, SA, SJ, SK, SQ, ST


class TrickPlayTests(TestCase):
    def player(self, id: int, cards: Cards) -> Player:
        player = Player(id, "", "")
        player._hand = cards
        return player

    def test_trick_play_enforce_non_empty(self) -> None:
        trick = Trick(4, Order(2))
        with self.assertRaises(PlayerError):
            trick.play(self.player(0, []), [])

    def test_trick_play_enforce_lead_suited(self) -> None:
        cases = [
            # Trumps and non-trump
            [S2, S3],
            # Two unsuited non-trump
            [S3, H3],
        ]

        for raw_cards in cases:
            with self.subTest(raw_cards=raw_cards):
                trick = Trick(4, Order(2))
                cards = initialize(raw_cards)
                with self.assertRaises(PlayerError):
                    trick.play(self.player(0, cards), cards)

    def test_trick_play_enforce_follow_length(self) -> None:
        trick = Trick(4, Order(2))
        cards = initialize([S3, S4, S5])
        player_0 = self.player(0, cards)
        player_1 = self.player(1, cards)
        self.assertIsNone(trick.play(player_0, cards[0:2]))
        with self.assertRaises(PlayerError):
            trick.play(player_1, cards[0:1])
        with self.assertRaises(PlayerError):
            trick.play(player_1, cards[0:3])
        self.assertIsNone(trick.play(player_1, cards[1:3]))

    def test_trick_play_enforce_follow_suit(self) -> None:
        cases = [
            # Full follow required, partial follow played
            (([S3, S4], [S3, S4, H3], [S4, H3]), False),
            # Full follow required, full follow played
            (([S3, S4], [S3, S4, H3], [S3, S4]), True),
            # Partial follow required, unsatisfied
            (([S3, S4], [S3, H4, H3], [H4, H3]), False),
            # Partial follow required, satisfied
            (([S3, S4], [S3, H4, H3], [S3, H3]), True),
            # Cannot follow, all trumps
            (([S3, S4], [S2, S2], [S2, S2]), True),
            # Cannot follow, non-trumps
            (([S3, S4], [H3, H3], [H3, H3]), True),
            # Cannot follow, mixed trumps
            (([S3, S4], [S2, H3], [S2, H3]), True),
            # Cannot follow, mixed non-trumps
            (([S3, S4], [S2, H3, H4], [H3, H4]), True),
            (([S3, S4], [H3, D3], [H3, D3]), True),
        ]
        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (lead, player, play) = tuple(map(initialize, setup))
                trick = Trick(4, Order(2))
                self.assertIsNone(trick.play(self.player(0, lead), lead))
                if expected:
                    self.assertIsNone(trick.play(self.player(1, player), play))
                else:
                    with self.assertRaises(PlayerError):
                        trick.play(self.player(1, player), play)

    def test_trick_play_enforce_format_for_matching_suits(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)
        cases = [
            # Trump followed by trumps, format enforced
            (([S3, S3, S4], [S5, S5, S6, S7], [1, 2, 3]), False),
            # Non-trump followed by trumps, format not enforced
            (([H3, H3, H4], [S5, S5, S6, S7], [1, 2, 3]), True),
            # Non-trump followed by matching non-trumps, format enforced
            (([H3, H3, H4], [H5, H5, H6, H7], [1, 2, 3]), False),
        ]
        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (lead, player, play) = setup
                lead = initialize(lead)
                player = initialize(player)
                play = [player[i] for i in play]
                trick = Trick(4, order)
                self.assertIsNone(trick.play(self.player(0, lead), lead))
                if expected:
                    self.assertIsNone(trick.play(self.player(1, player), play))
                else:
                    with self.assertRaises(PlayerError):
                        trick.play(self.player(1, player), play)

    def test_trick_winner_resolution(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)
        cases = [
            # Losing - follow with mixed suits
            [([S2, S3], 0), ([S2, H3], 0)],
            [([H3, H6], 0), ([H3, S5], 0)],
            # Losing - follow trump with non-trumps
            [([S3], 0), ([H4], 0)],
            # Losing - follow non-trump with mismatching non-trumps
            [([H3], 0), ([D4], 0)],
            [([JB, SA], 0), ([H3, D3], 0)],
            # Losing - follow with legal but mismatching format
            [([S3, S3, S4], 0), ([S3, S4, S5], 0)],
            # Winning - suited
            [([S3], 0), ([S2], 1)],
            [([H3], 0), ([H4], 1)],
            # Winning - trumped
            [([H4], 0), ([S4], 1)],
            # Winning - lead format maintained:
            # Two pairs => tractor => two pairs
            [([S3, S3, S5, S5], 0), ([S6, S6, S7, S7], 1), ([S8, S8, ST, ST], 2)],
        ]
        for steps in cases:
            with self.subTest(steps=steps):
                trick = Trick(4, order)
                for player, (raw_play, winner) in enumerate(steps):
                    play = initialize(raw_play)
                    self.assertIsNone(trick.play(self.player(player, play), play))
                    self.assertEqual(winner, trick.winner_pid)

    def test_trick_play_accumulates_score(self) -> None:
        trick = Trick(4, Order(2))
        cards = initialize([SA, S3, S4, S5, S6, S7, S8, S9, ST, SJ, SQ, SK])
        self.assertIsNone(trick.play(self.player(0, cards), cards))
        self.assertEqual(25, trick.score)
