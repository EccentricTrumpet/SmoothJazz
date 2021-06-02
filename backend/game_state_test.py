import unittest
from game_state import *

class HandTests(unittest.TestCase):

    def test_detects_pair(self):
        hand = Hand([SJCard(2), SJCard(2)])
        self.assertEqual(hand.type, "PAIR")

if __name__ == '__main__':
    unittest.main()