from unittest import TestCase
from abstractions.enums import Suit
from core.trick import Trick
from core.order import Order
from core.player import Player
from test.utils import initialize
from test.spades import S2, S3, S4, S5, S6, S7, S8, S9, SA, SJ, SK, SQ, ST
from test.hearts import H3, H4, H6
from test.diamonds import D3, D4


class TrickPlayTests(TestCase):

    def test_trick_play_enforce_non_empty(self) -> None:
        trick = Trick(4, Order(2))
        self.assertFalse(trick.try_play([], Player(0, "", "", []), []))

    def test_trick_play_enforce_possession(self) -> None:
        trick = Trick(4, Order(2))
        cards = initialize([S2, S3])
        hand = [cards[0]]
        play = [cards[1]]
        self.assertFalse(trick.try_play([], Player(0, "", "", hand), play))

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
                self.assertFalse(trick.try_play([], Player(0, "", "", cards), cards))

    def test_trick_play_enforce_follow_length(self) -> None:
        trick = Trick(4, Order(2))
        cards = initialize([S3, S4, S5])
        player_0 = Player(0, "", "", cards)
        player_1 = Player(1, "", "", cards)
        self.assertTrue(trick.try_play([], player_0, cards[0:2]))
        self.assertFalse(trick.try_play([], player_1, cards[0:1]))
        self.assertFalse(trick.try_play([], player_1, cards[0:3]))
        self.assertTrue(trick.try_play([], player_1, cards[1:3]))

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
                self.assertTrue(trick.try_play([], Player(0, "", "", lead), lead))
                self.assertEqual(
                    expected, trick.try_play([], Player(1, "", "", player), play)
                )

    def test_trick_winner_resolution(self) -> None:
        order = Order(2)
        order.reset(Suit.SPADE)
        cases = [
            # Losing - follow with mixed suits
            [([S2, S3], True, 0), ([S2, H3], True, 0)],
            [([H3, H6], True, 0), ([H3, S5], True, 0)],
            # Losing - follow trump with non-trumps
            [([S3], True, 0), ([H4], True, 0)],
            # Losing - follow non-trump with mismatching non-trumps
            [([H3], True, 0), ([D4], True, 0)],
            # Winning - suited
            [([S3], True, 0), ([S2], True, 1)],
            [([H3], True, 0), ([H4], True, 1)],
            # Winning - trumped
            [([H4], True, 0), ([S4], True, 1)],
            # Test two pairs => tractor => two pairs plays to ensure third player can win
        ]
        for steps in cases:
            with self.subTest(steps=steps):
                trick = Trick(4, order)
                for player, (raw_play, legal, winner) in enumerate(steps):
                    play = initialize(raw_play)
                    self.assertEqual(
                        legal, trick.try_play([], Player(player, "", "", play), play)
                    )
                    self.assertEqual(winner, trick.winner_id)

    def test_trick_play_accumulates_score(self) -> None:
        trick = Trick(4, Order(2))
        cards = initialize([SA, S3, S4, S5, S6, S7, S8, S9, ST, SJ, SQ, SK])
        self.assertTrue(trick.try_play([], Player(0, "", "", cards), cards))
        self.assertEqual(25, trick.score)
