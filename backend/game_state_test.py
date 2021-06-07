import unittest
from game_state import (
    Card,
    Hand,
    Suit)

class HandTests(unittest.TestCase):

    def test_detects_pair(self) -> None:
        hand = Hand([Card(Suit.SPADES, 2), Card(Suit.SPADES, 2)])
        self.assertEqual(hand.type, "PAIR")

if __name__ == '__main__':
    unittest.main()