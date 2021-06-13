import unittest
from game_state import (
    Hand,
    Player,
    Suit,
    Rank,
    Game,
    GameState,
    Player,
    create_cardproto)

class HandTests(unittest.TestCase):

    def test_detects_pair(self) -> None:
        hand = Hand([
            create_cardproto(Suit.SPADES, Rank.KING),
            create_cardproto(Suit.SPADES, Rank.KING)])
        self.assertEqual(hand.type, "PAIR")

class PlayerTests(unittest.TestCase):

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


class GameTests(unittest.TestCase):

    def __addCardsToHand(self, player: Player, hand: Hand) -> None:
        for card in hand:
            player.add_card(card)

    def test_declare_trump(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = game.add_player('player_1', True)
        hand = [Card(Suit.SPADES, 2)]
        self.__addCardsToHand(p1, hand)

        # player_1 declares trump
        success, err = game.play('player_1', [Card(Suit.SPADES, 2)])
        p1_add_player_update = next(p1.update_stream())
        p1_declare_trump_update = next(p1.update_stream())

        self.assertTrue(success)
        self.assertEqual(err, '')
        self.assertEqual(p1_declare_trump_update.trump_player_id, "player_1")
        self.assertEqual(p1_declare_trump_update.trump_cards, "player_1")

if __name__ == '__main__':
    unittest.main()
