# To run individual test cases, do `python3 backend/game_state_test.py GameTests.test_hide_kitty_incorrect_number_of_cards`
import unittest
import timeout_decorator
from shengji_pb2 import (
    Hand as HandProto,
    Game as GameProto,
    Card as CardProto)
from typing import Sequence
from game_state import (
    Player,
    Ranking,
    Suit,
    Rank,
    Game,
    GameState,
    Player,
    Tractor,
    Trick,
    TrickFormat)

SPADE_TWO_PROTO = CardProto(suit=Suit.SPADES,rank=Rank.TWO)
SPADE_KING_PROTO = CardProto(suit=Suit.SPADES,rank=Rank.KING)
SMALL_JOKER_PROTO = CardProto(suit=Suit.SMALL_JOKER,rank=Rank.RANK_UNDEFINED)
BIG_JOKER_PROTO = CardProto(suit=Suit.BIG_JOKER,rank=Rank.RANK_UNDEFINED)
HEART_TWO_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.TWO)

class TrickFormatTests(unittest.TestCase):

    @timeout_decorator.timeout(20)
    def verify_equivalent_format(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2))
        format1.pairs.append()
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertTrue(format1.verify(format2))

    @timeout_decorator.timeout(20)
    def verify_unequal_tractors_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2))
        format1.pairs.append()
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2))
        format2.tractors.append(Tractor(SPADE_TWO_PROTO, 2))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertFalse(format1.verify(format2))

    @timeout_decorator.timeout(20)
    def verify_unequal_tractor_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2))
        format1.pairs.append()
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 3))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertFalse(format1.verify(format2))

    @timeout_decorator.timeout(20)
    def verify_unequal_pairs_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2))
        format1.pairs.append()
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.pairs.append(SPADE_TWO_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertFalse(format1.verify(format2))

    @timeout_decorator.timeout(20)
    def verify_unequal_singles_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2))
        format1.pairs.append()
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        format2.singles.append(SPADE_TWO_PROTO)
        self.assertFalse(format1.verify(format2))

class TrickTests(unittest.TestCase):

    @timeout_decorator.timeout(20)
    def create_format_singles(self) -> None:
        cards = [SMALL_JOKER_PROTO, SPADE_TWO_PROTO, SPADE_KING_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick = Trick(ranking)
        format = trick.createFormat(cards)

        self.assertTrue(format.isTrump)
        self.assertEqual(3, format.length)
        self.assertEqual(3, len(format.singles))
        self.assertEqual(0, len(format.pairs))
        self.assertEqual(0, len(format.tractors))

    @timeout_decorator.timeout(20)
    def create_format_pairs(self) -> None:
        cards = [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO, SPADE_KING_PROTO, SPADE_KING_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick = Trick(ranking)
        format = trick.createFormat(cards)

        self.assertTrue(format.isTrump)
        self.assertEqual(4, format.length)
        self.assertEqual(0, len(format.singles))
        self.assertEqual(2, len(format.pairs))
        self.assertEqual(0, len(format.tractors))

    @timeout_decorator.timeout(20)
    def create_format_tractors(self) -> None:
        cards = [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO, SPADE_TWO_PROTO, SPADE_TWO_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick = Trick(ranking)
        format = trick.createFormat(cards)

        self.assertTrue(format.isTrump)
        self.assertEqual(4, format.length)
        self.assertEqual(0, len(format.singles))
        self.assertEqual(0, len(format.pairs))
        self.assertEqual(1, len(format.tractors))

    @timeout_decorator.timeout(20)
    def create_format_mixed(self) -> None:
        cards = [BIG_JOKER_PROTO, BIG_JOKER_PROTO, SMALL_JOKER_PROTO, SMALL_JOKER_PROTO, SPADE_TWO_PROTO, HEART_TWO_PROTO, HEART_TWO_PROTO, SPADE_KING_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick = Trick(ranking)
        format = trick.createFormat(cards)

        self.assertTrue(format.isTrump)
        self.assertEqual(8, format.length)
        self.assertEqual(2, len(format.singles))
        self.assertEqual(1, len(format.pairs))
        self.assertEqual(1, len(format.tractors))

class PlayerTests(unittest.TestCase):

    @timeout_decorator.timeout(20)
    def test_player_has_card(self) -> None:
        player = Player(Ranking(2), "player", False)

        player.add_card(SPADE_KING_PROTO)
        self.assertTrue(player.has_cards([SPADE_KING_PROTO]))

    @timeout_decorator.timeout(20)
    def test_player_does_not_have_cards(self) -> None:
        player = Player(Ranking(2), "player", False)

        player.add_card(SPADE_KING_PROTO)
        self.assertFalse(player.has_cards([SPADE_KING_PROTO, SPADE_KING_PROTO]))

    @timeout_decorator.timeout(20)
    def test_player_remove_card(self) -> None:
        player = Player(Ranking(2), "player", False)

        player.add_card(SPADE_KING_PROTO)
        self.assertEqual(1, len(player.hand))

        player.remove_card(SPADE_KING_PROTO)
        self.assertEqual(0, len(player.hand))


class GameTests(unittest.TestCase):

    def __createPlayerWithHand(self, game: Game, player_name: str, hand: Sequence[CardProto]) -> Player:
        new_player = game.add_player(player_name, True)
        next(new_player.update_stream()) # ignore the add_player update
        for card in hand:
            new_player.add_card(card)
        return new_player

    def __playHandAndAssertSuccess(self, game: Game, player_name: str, cards: Sequence[CardProto]) -> None:
        success, err = game.play(player_name, cards)
        self.assertEqual(err, '')
        self.assertTrue(success)

    def __assertUpdateHasTrumpStatus(self, game_proto: GameProto, expected_trump_player_name: str, expected_trump_cards: Sequence[CardProto]) -> None:
        self.assertEqual(game_proto.trump_player_name, expected_trump_player_name)
        self.assertEqual(game_proto.kitty_player_name, expected_trump_player_name)
        self.assertEqual(game_proto.trump_cards, HandProto(cards=expected_trump_cards))

    @timeout_decorator.timeout(20)
    def test_declare_valid_trump(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [SPADE_TWO_PROTO])

    @timeout_decorator.timeout(20)
    def test_declare_invalid_trump_card_not_in_hand(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO])

        # player_1 declares a trump card that they don't have.
        success, err = game.play('player_1', [SPADE_TWO_PROTO])
        self.assertRegex(err, 'Player does not possess the cards.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(20)
    def test_declare_invalid_trump_wrong_rank(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO])

        # player_1 declares a trump card that doesn't match current trump rank
        success, err = game.play('player_1', [SPADE_KING_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(20)
    def test_declare_invalid_trump_single_too_small(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO])
        # player_2 declares a trump card that's too small
        success, err = game.play('player_2', [HEART_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(20)
    def test_declare_valid_double_trump_overwrite(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        # player_2 overwrites player_1's trump card with two 红桃二
        self.__playHandAndAssertSuccess(game, 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])

    @timeout_decorator.timeout(20)
    def test_declare_invalid_double_trump_diff_cards(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, HEART_TWO_PROTO])

        success, err = game.play('player_1', [SPADE_TWO_PROTO, HEART_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(20)
    def test_declare_invalid_double_trump_wrong_rank(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO, SPADE_KING_PROTO])

        success, err = game.play('player_1', [SPADE_KING_PROTO, SPADE_KING_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(20)
    def test_declare_valid_trump_with_small_jokers(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

    @timeout_decorator.timeout(20)
    def test_declare_valid_trump_small_joker_overwrites(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

    @timeout_decorator.timeout(20)
    def test_declare_valid_trump_big_joker_overwrites(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])

    @timeout_decorator.timeout(20)
    def test_declare_trump_with_three_cards(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        success, err = game.play('player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO, SPADE_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(20)
    def test_declare_trump_cannot_overwrite_self_declaration(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO, SPADE_TWO_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        success, err = game.play('player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite their previous declaration:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(20)
    def test_declare_trump_fortify_self_declaration(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [HEART_TWO_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])

    @timeout_decorator.timeout(20)
    def test_declare_trump_pair_with_only_one_card_in_hand(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])

        success, err = game.play('player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])

        self.assertFalse(success)
        self.assertRegex(err, 'Player does not possess the cards.*')

    @timeout_decorator.timeout(20)
    def test_hide_kitty_not_turn_of_player(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])

        game._next_player_name = 'creator'
        success, err = game.play('player_1', [HEART_TWO_PROTO])

        self.assertFalse(success)
        self.assertRegex(err, 'Not the turn of player player_1')

    @timeout_decorator.timeout(20)
    def test_hide_kitty_incorrect_number_of_cards(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [HEART_TWO_PROTO])

        self.assertFalse(success)
        self.assertRegex(err, 'Incorrect number of cards to hide')

    @timeout_decorator.timeout(20)
    def test_hide_kitty_player_not_possess_cards(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [HEART_TWO_PROTO]*8)

        self.assertFalse(success)
        self.assertRegex(err, 'Player does not possess the cards:.*')

    @timeout_decorator.timeout(20)
    def test_hide_kitty_valid(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO]*8)
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO]*8)

        game_proto = next(p1.update_stream())
        self.assertEqual(list(game_proto.kitty.cards), [HEART_TWO_PROTO]*8)
        self.assertEqual(game_proto.next_turn_player_name, 'player_1')

    @timeout_decorator.timeout(20)
    def test_play_hand_not_possess_cards(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.PLAY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO]*2)
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [SPADE_KING_PROTO]*2)

        self.assertFalse(success)
        self.assertRegex(err, 'Player does not possess the cards:.*')

    @timeout_decorator.timeout(20)
    def test_play_hand_valid(self) -> None:
        game = Game('creator', '0', 0)
        game.state = GameState.PLAY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO]*2)
        p2 = self.__createPlayerWithHand(game, 'player_2', [SPADE_TWO_PROTO]*2)
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO])

        game_proto = next(p2.update_stream())
        self.assertEqual(game_proto.next_turn_player_name, 'player_2')
        self.assertEqual(game_proto.players[0].current_round_trick, HandProto(cards=[HEART_TWO_PROTO]))


if __name__ == '__main__':
    unittest.main()
