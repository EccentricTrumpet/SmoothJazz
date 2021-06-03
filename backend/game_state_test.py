import unittest
from game_state import (
    Card,
    Hand)

class HandTests(unittest.TestCase):

    def test_detects_pair(self) -> None:
        hand = Hand([Card(2), Card(2)])
        self.assertEqual(hand.type, "PAIR")

if __name__ == '__main__':
    unittest.main()