import unittest
from shengji_pb2 import (
    Hand as HandProto,
    Game as GameProto,
    Card as CardProto)
from typing import Sequence
from game_state import (
    Hand,
    Player,
    Suit,
    Rank,
    Game,
    GameState,
    Player)

SPADE_TWO_PROTO = CardProto(suit=Suit.SPADES,rank=Rank.TWO)
SPADE_KING_PROTO = CardProto(suit=Suit.SPADES,rank=Rank.KING)
SMALL_JOKER_PROTO = CardProto(suit=Suit.SMALL_JOKER,rank=Rank.RANK_UNDEFINED)
SMALL_JOKER_RANK_TWO_PROTO = CardProto(suit=Suit.SMALL_JOKER,rank=Rank.TWO)
BIG_JOKER_PROTO = CardProto(suit=Suit.BIG_JOKER,rank=Rank.RANK_UNDEFINED)
BIG_JOKER_RANK_TWO_PROTO = CardProto(suit=Suit.BIG_JOKER,rank=Rank.TWO)
HEART_TWO_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.TWO)

class HandTests(unittest.TestCase):

    def test_detects_pair(self) -> None:
        hand = Hand([SPADE_KING_PROTO, SPADE_KING_PROTO])
        self.assertEqual(hand.type, "PAIR")

class PlayerTests(unittest.TestCase):

    def test_player_has_card(self) -> None:
        player = Player("player", False)

        player.add_card(SPADE_KING_PROTO)
        self.assertTrue(player.has_card(SPADE_KING_PROTO))

    def test_player_remove_card(self) -> None:
        player = Player("player", False)

        player.add_card(SPADE_KING_PROTO)
        self.assertEqual(1, len(player.cards_on_hand))

        player.remove_card(SPADE_KING_PROTO)
        self.assertEqual(0, len(player.cards_on_hand))


class GameTests(unittest.TestCase):

    def __createPlayerWithHand(self, game: Game, player_id: str, hand: Sequence[CardProto]) -> Player:
        new_player = game.add_player(player_id, True)
        next(new_player.update_stream()) # ignore the add_player update
        for card in hand:
            new_player.add_card(card)
        return new_player

    def __playHandAndAssertSuccess(self, game: Game, player_id: str, cards: Sequence[CardProto]) -> None:
        success, err = game.play(player_id, cards)
        self.assertEqual(err, '')
        self.assertTrue(success)

    def __assertUpdateHasTrumpStatus(self, game_proto: GameProto, expected_trump_player_id: str, expected_trump_cards: Sequence[CardProto]) -> None:
        self.assertEqual(game_proto.trump_player_id, expected_trump_player_id)
        self.assertEqual(game_proto.trump_cards, HandProto(cards=expected_trump_cards))

    def test_declare_valid_trump(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [SPADE_TWO_PROTO])

    def test_declare_invalid_trump_card_not_in_hand(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO])

        # player_1 declares a trump card that they don't have.
        success, err = game.play('player_1', [SPADE_TWO_PROTO])
        self.assertRegex(err, 'Player does not possess the card suit:.*')
        self.assertFalse(success)

    def test_declare_invalid_trump_wrong_rank(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO])

        # player_1 declares a trump card that doesn't match current trump rank
        success, err = game.play('player_1', [SPADE_KING_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    def test_declare_invalid_trump_single_too_small(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO])
        # player_2 declares a trump card that's too small
        success, err = game.play('player_2', [HEART_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    def test_declare_valid_double_trump_overwrite(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        # player_2 overwrites player_1's trump card with two 红桃二
        self.__playHandAndAssertSuccess(game, 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])

    def test_declare_invalid_double_trump_diff_cards(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, HEART_TWO_PROTO])

        success, err = game.play('player_1', [SPADE_TWO_PROTO, HEART_TWO_PROTO])
        self.assertRegex(err, 'Trump declaration cards do not match:.*')
        self.assertFalse(success)

    def test_declare_invalid_double_trump_wrong_rank(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO, SPADE_KING_PROTO])

        success, err = game.play('player_1', [SPADE_KING_PROTO, SPADE_KING_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    def test_declare_valid_trump_with_small_jokers(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [SMALL_JOKER_RANK_TWO_PROTO, SMALL_JOKER_RANK_TWO_PROTO])

    def test_declare_valid_trump_small_joker_overwrites(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [SMALL_JOKER_RANK_TWO_PROTO, SMALL_JOKER_RANK_TWO_PROTO])

    def test_declare_valid_trump_big_joker_overwrites(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [BIG_JOKER_RANK_TWO_PROTO, BIG_JOKER_RANK_TWO_PROTO])

    def test_declare_trump_with_three_cards(self) -> None:
        game = Game('creator', '0', 0.001)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        success, err = game.play('player_1', [SPADE_TWO_PROTO, SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.assertRegex(err, 'Too many trump declaration cards:.*')
        self.assertFalse(success)


if __name__ == '__main__':
    unittest.main()
