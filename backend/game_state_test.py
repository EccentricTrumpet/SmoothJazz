import unittest
from game_state import (
    Hand,
    Player,
    Suit,
    Rank,
    create_cardproto)

class HandTests(unittest.TestCase):

    def test_detects_pair(self) -> None:
        hand = Hand([
            create_cardproto(Suit.SPADES, Rank.KING),
            create_cardproto(Suit.SPADES, Rank.KING)])
        self.assertEqual(hand.type, "PAIR")

    def test_player_has_card(self) -> None:
        player = Player("player", False)

        player.add_card(create_cardproto(Suit.SPADES, Rank.KING))
        self.assertTrue(player.has_card(create_cardproto(Suit.SPADES, Rank.KING)))

    def test_player_remove_card(self) -> None:
        player = Player("player", False)

        player.add_card(create_cardproto(Suit.SPADES, Rank.KING))
        self.assertEqual(1, len(player.cards_on_hand))

        player.remove_card(create_cardproto(Suit.SPADES, Rank.KING))
        self.assertEqual(0, len(player.cards_on_hand))

if __name__ == '__main__':
    unittest.main()