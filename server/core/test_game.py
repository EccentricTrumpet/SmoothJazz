from unittest import TestCase
from core.format import Format
from core.game import Game
from core import Order, Player
from core.trick import Trick
from testing import initialize, JB, JR
from testing.spades import S2, S5


class GameTests(TestCase):
    def test_end_players_level_up(self) -> None:
        cases = [
            # Attackers + 4
            (([6, 6, 6, 6], 275), ([6, 10, 6, 10], 1)),
            (([6, 6, 6, 6], 240), ([6, 10, 6, 10], 1)),
            # Attackers + 3
            (([6, 6, 6, 6], 235), ([6, 9, 6, 9], 1)),
            (([6, 6, 6, 6], 200), ([6, 9, 6, 9], 1)),
            # Attackers + 2
            (([6, 6, 6, 6], 195), ([6, 8, 6, 8], 1)),
            (([6, 6, 6, 6], 160), ([6, 8, 6, 8], 1)),
            # Attackers + 1
            (([6, 6, 6, 6], 155), ([6, 7, 6, 7], 1)),
            (([6, 6, 6, 6], 120), ([6, 7, 6, 7], 1)),
            # Attackers
            (([6, 6, 6, 6], 115), ([6, 6, 6, 6], 1)),
            (([6, 6, 6, 6], 80), ([6, 6, 6, 6], 1)),
            # Defenders + 1
            (([5, 5, 5, 5], 75), ([6, 5, 6, 5], 2)),
            (([5, 5, 5, 5], 40), ([6, 5, 6, 5], 2)),
            # Defenders + 2
            (([5, 5, 5, 5], 35), ([7, 5, 7, 5], 2)),
            (([5, 5, 5, 5], 5), ([7, 5, 7, 5], 2)),
            # Defenders + 3
            (([5, 5, 5, 5], 0), ([8, 5, 8, 5], 2)),
            (([5, 5, 5, 5], -35), ([8, 5, 8, 5], 2)),
            # Defenders + 4
            (([5, 5, 5, 5], -40), ([9, 5, 9, 5], 2)),
            (([5, 5, 5, 5], -75), ([9, 5, 9, 5], 2)),
            # Defenders + 5
            (([5, 5, 5, 5], -80), ([10, 5, 10, 5], 2)),
            (([5, 5, 5, 5], -115), ([10, 5, 10, 5], 2)),
            # Boss levels
            (([2, 2, 2, 2], 120), ([2, 2, 2, 2], 1)),
            (([6, 6, 6, 6], 280), ([6, 10, 6, 10], 1)),
            (([5, 5, 5, 5], -120), ([10, 5, 10, 5], 2)),
        ]
        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (start_levels, score) = setup
                (next_levels, next_lead) = expected

                players = [Player(i, "", "", []) for i in range(4)]
                for player, level in zip(players, start_levels):
                    player.level = level
                game = Game(0, 0, 2, 0, players)
                game._tricks.append(Trick(4, Order(2)))

                # Set protected fields
                game._score = score
                game._defenders.add(0)
                game._attackers.add(1)
                game._defenders.add(2)
                game._attackers.add(3)

                game._end()

                self.assertEqual(next_lead, game.next_lead_id)
                for player, level in zip(players, next_levels):
                    self.assertEqual(level, player.level)

    def test_end_adds_kitty_score(self) -> None:
        cases = [
            # Defender
            (([JR, JR, JR, JR, JR, JR, JR, JR, S5], [JR], 0), 0),
            # Single
            (([JR, JR, JR, JR, JR, JR, JR, JR, S5], [JR], 1), 10),
            # Pair
            (([JR, JR, JR, JR, JR, JR, JR, JR, S5], [JR, JR], 1), 20),
            # Tractors
            (([JR, JR, JR, JR, JR, JR, JR, JR, S5], [JR, JR, JB, JB], 1), 40),
            (([JR, JR, JR, JR, JR, JR, JR, JR, S5], [JR, JR, JB, JB, S2, S2], 1), 80),
        ]
        for setup, expected in cases:
            with self.subTest(setup=setup, expected=expected):
                (raw_kitty, raw_play, player) = setup
                kitty = initialize(raw_kitty)
                play = initialize(raw_play)

                order = Order(2)
                players = [Player(i, "", "", []) for i in range(2)]
                game = Game(0, 0, 2, 0, players)
                trick = Trick(4, order)
                trick.winner_id = player
                trick._plays[player] = Format(order, play)
                game._tricks.append(trick)

                # Set protected fields
                game._kitty = kitty
                game._defenders.add(0)
                game._attackers.add(1)

                game._end()

                self.assertEqual(expected, game._score)
