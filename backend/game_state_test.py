# To run individual test cases, do `python3 backend/game_state_test.py GameTests.test_hide_kitty_incorrect_number_of_cards`
import logging
import sys
import argparse
import timeout_decorator
import unittest
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
SPADE_TEN_PROTO = CardProto(suit=Suit.SPADES,rank=Rank.TEN)
SPADE_KING_PROTO = CardProto(suit=Suit.SPADES,rank=Rank.KING)
SPADE_ACE_PROTO = CardProto(suit=Suit.SPADES,rank=Rank.ACE)
SMALL_JOKER_PROTO = CardProto(suit=Suit.SMALL_JOKER,rank=Rank.RANK_UNDEFINED)
BIG_JOKER_PROTO = CardProto(suit=Suit.BIG_JOKER,rank=Rank.RANK_UNDEFINED)
HEART_TWO_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.TWO)
HEART_QUEEN_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.QUEEN)
HEART_KING_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.KING)
HEART_TEN_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.TEN)
HEART_FIVE_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.FIVE)
HEART_ACE_PROTO = CardProto(suit=Suit.HEARTS,rank=Rank.ACE)
DEFAULT_TEST_TIMEOUT = 20

class TrickFormatTests(unittest.TestCase):

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_verify_equivalent_format(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2, []))
        format1.pairs.append(BIG_JOKER_PROTO)
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2, []))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertTrue(format1.verify(format2))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_verify_unequal_tractors_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2, []))
        format1.pairs.append(BIG_JOKER_PROTO)
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2, []))
        format2.tractors.append(Tractor(SPADE_TWO_PROTO, 2, []))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertFalse(format1.verify(format2))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_verify_unequal_tractor_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2, []))
        format1.pairs.append(BIG_JOKER_PROTO)
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 3, []))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertFalse(format1.verify(format2))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_verify_unequal_pairs_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2, []))
        format1.pairs.append(BIG_JOKER_PROTO)
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2, []))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.pairs.append(SPADE_TWO_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        self.assertFalse(format1.verify(format2))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_verify_unequal_singles_lengths(self) -> None:
        format1 = TrickFormat(Suit.SPADES, 7, True)
        format1.tractors.append(Tractor(SPADE_KING_PROTO, 2, []))
        format1.pairs.append(BIG_JOKER_PROTO)
        format1.singles.append(HEART_TWO_PROTO)
        format2 = TrickFormat(Suit.SPADES, 7, True)
        format2.tractors.append(Tractor(HEART_TWO_PROTO, 2, []))
        format2.pairs.append(BIG_JOKER_PROTO)
        format2.singles.append(SMALL_JOKER_PROTO)
        format2.singles.append(SPADE_TWO_PROTO)
        self.assertFalse(format1.verify(format2))

class TrickTests(unittest.TestCase):

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_create_empty_format(self) -> None:
        cards = []
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick_format = Trick(ranking).create_format(cards)

        self.assertTrue(TrickFormat.is_invalid(trick_format))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_create_format_singles(self) -> None:
        cards = [SMALL_JOKER_PROTO, SPADE_TWO_PROTO, SPADE_KING_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick_format = Trick(ranking).create_format(cards)

        self.assertTrue(trick_format.is_trump)
        self.assertEqual(3, trick_format.length)
        self.assertEqual(3, len(trick_format.singles))
        self.assertEqual(0, len(trick_format.pairs))
        self.assertEqual(0, len(trick_format.tractors))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_create_format_pairs(self) -> None:
        cards = [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO, SPADE_KING_PROTO, SPADE_KING_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick_format = Trick(ranking).create_format(cards)

        self.assertTrue(trick_format.is_trump)
        self.assertEqual(4, trick_format.length)
        self.assertEqual(0, len(trick_format.singles))
        self.assertEqual(2, len(trick_format.pairs))
        self.assertEqual(0, len(trick_format.tractors))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_create_format_tractors(self) -> None:
        cards = [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO, SPADE_TWO_PROTO, SPADE_TWO_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick_format = Trick(ranking).create_format(cards)

        self.assertTrue(trick_format.is_trump)
        self.assertEqual(4, trick_format.length)
        self.assertEqual(0, len(trick_format.singles))
        self.assertEqual(0, len(trick_format.pairs))
        self.assertEqual(1, len(trick_format.tractors))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def tst_create_format_mixed(self) -> None:
        cards = [BIG_JOKER_PROTO, BIG_JOKER_PROTO, SMALL_JOKER_PROTO, SMALL_JOKER_PROTO, SPADE_TWO_PROTO, HEART_TWO_PROTO, HEART_TWO_PROTO, SPADE_KING_PROTO]
        ranking = Ranking(2)
        ranking.resetOrder(Suit.SPADES)
        trick_format = Trick(ranking).create_format(cards)

        self.assertTrue(trick_format.isTrump)
        self.assertEqual(8, trick_format.length)
        self.assertEqual(2, len(trick_format.singles))
        self.assertEqual(1, len(trick_format.pairs))
        self.assertEqual(1, len(trick_format.tractors))

class PlayerTests(unittest.TestCase):

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_player_has_card(self) -> None:
        player = Player(Ranking(2), "player", False)

        player.add_card(SPADE_KING_PROTO)
        self.assertTrue(player.has_cards([SPADE_KING_PROTO]))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_player_does_not_have_cards(self) -> None:
        player = Player(Ranking(2), "player", False)

        player.add_card(SPADE_KING_PROTO)
        self.assertFalse(player.has_cards([SPADE_KING_PROTO, SPADE_KING_PROTO]))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
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

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_valid_trump(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [SPADE_TWO_PROTO])

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_invalid_trump_card_not_in_hand(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO])

        # player_1 declares a trump card that they don't have.
        success, err = game.play('player_1', [SPADE_TWO_PROTO])
        self.assertRegex(err, 'Player does not possess the cards.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_invalid_trump_wrong_rank(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO])

        # player_1 declares a trump card that doesn't match current trump rank
        success, err = game.play('player_1', [SPADE_KING_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_invalid_trump_single_too_small(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO])
        # player_2 declares a trump card that's too small
        success, err = game.play('player_2', [HEART_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_valid_double_trump_overwrite(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        # player_2 overwrites player_1's trump card with two 红桃二
        self.__playHandAndAssertSuccess(game, 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [HEART_TWO_PROTO, HEART_TWO_PROTO])

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_invalid_double_trump_diff_cards(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, HEART_TWO_PROTO])

        success, err = game.play('player_1', [SPADE_TWO_PROTO, HEART_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_invalid_double_trump_wrong_rank(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_KING_PROTO, SPADE_KING_PROTO])

        success, err = game.play('player_1', [SPADE_KING_PROTO, SPADE_KING_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_valid_trump_with_small_jokers(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_valid_trump_small_joker_overwrites(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_valid_trump_big_joker_overwrites(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        # player_1 declares a valid trump card.
        self.__playHandAndAssertSuccess(game, 'player_1', [SMALL_JOKER_PROTO, SMALL_JOKER_PROTO])

        p2 = self.__createPlayerWithHand(game, 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p2.update_stream()), 'player_2', [BIG_JOKER_PROTO, BIG_JOKER_PROTO])

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_trump_with_three_cards(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO, SPADE_TWO_PROTO])

        success, err = game.play('player_1', [SPADE_TWO_PROTO, SPADE_TWO_PROTO, SPADE_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite current trump:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_trump_cannot_overwrite_self_declaration(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO, SPADE_TWO_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [SPADE_TWO_PROTO])

        success, err = game.play('player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        self.assertRegex(err, f'.*Cannot overwrite their previous declaration:.*')
        self.assertFalse(success)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_trump_fortify_self_declaration(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [HEART_TWO_PROTO])

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])
        self.__assertUpdateHasTrumpStatus(next(p1.update_stream()), 'player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_declare_trump_pair_with_only_one_card_in_hand(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.DEAL
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])

        success, err = game.play('player_1', [HEART_TWO_PROTO, HEART_TWO_PROTO])

        self.assertFalse(success)
        self.assertRegex(err, 'Player does not possess the cards.*')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_hide_kitty_not_turn_of_player(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])
        self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO])

        game._next_player_name = 'player_2'
        success, err = game.play('player_1', [HEART_TWO_PROTO])

        self.assertFalse(success)
        self.assertRegex(err, 'Not the turn of player player_1')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_hide_kitty_incorrect_number_of_cards(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [HEART_TWO_PROTO])

        self.assertFalse(success)
        self.assertRegex(err, 'Incorrect number of cards to hide')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_hide_kitty_player_not_possess_cards(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO])
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [HEART_TWO_PROTO]*8)

        self.assertFalse(success)
        self.assertRegex(err, 'Player does not possess the cards:.*')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_hide_kitty_valid(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.HIDE_KITTY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO]*8)
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO]*8)

        game_proto = next(p1.update_stream())
        self.assertEqual(list(game_proto.kitty.cards), [HEART_TWO_PROTO]*8)
        self.assertEqual(game_proto.next_turn_player_name, 'player_1')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_not_possess_cards(self) -> None:
        game = Game('player_1', '0', 0)
        game.state = GameState.PLAY
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO]*2)
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [SPADE_KING_PROTO]*2)

        self.assertFalse(success)
        self.assertRegex(err, 'Player does not possess the cards:.*')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_not_following_suit(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_KING_PROTO]*2)
        p2 = self.__createPlayerWithHand(game, 'player_2', [SPADE_KING_PROTO]*2 + [HEART_QUEEN_PROTO])
        game.state = GameState.PLAY
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_KING_PROTO])

        success, err = game.play('player_2', [SPADE_KING_PROTO])
        self.assertFalse(success)
        self.assertRegex(err, 'Not all playable cards of the lead suit were played.*')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_invalid_toss_leave_smallest_on_table(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_QUEEN_PROTO, HEART_ACE_PROTO])
        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_KING_PROTO, HEART_QUEEN_PROTO])
        game.state = GameState.PLAY
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [HEART_QUEEN_PROTO, HEART_ACE_PROTO])
        self.assertRegex(err, '(?s)Player cards are not the largest, leaving smallest on the table.*QUEEN.*')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_valid_multi_toss(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_KING_PROTO, HEART_ACE_PROTO, HEART_QUEEN_PROTO])
        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TWO_PROTO, SPADE_ACE_PROTO, SMALL_JOKER_PROTO])
        game.state = GameState.PLAY
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_KING_PROTO, HEART_ACE_PROTO])

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_invalid_trump_toss(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [BIG_JOKER_PROTO, HEART_TWO_PROTO])
        p2 = self.__createPlayerWithHand(game, 'player_2', [SMALL_JOKER_PROTO, HEART_QUEEN_PROTO])
        game.state = GameState.PLAY
        game._next_player_name = 'player_1'

        success, err = game.play('player_1', [BIG_JOKER_PROTO, HEART_TWO_PROTO])
        self.assertRegex(err, '(?s)Player cards are not the largest, leaving smallest on the table.*TWO.*')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_lead_player_winning_with_correct_score(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_KING_PROTO]*2)
        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_TEN_PROTO, HEART_FIVE_PROTO])
        game.state = GameState.PLAY
        game._kitty_player_name = 'player_1'
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_KING_PROTO]*2)
        self.__playHandAndAssertSuccess(game, 'player_2', [HEART_FIVE_PROTO, HEART_TEN_PROTO])

        self.assertEqual(game._next_player_name, 'player_1')
        self.assertEqual(p1.score, 35)
        self.assertEqual(p2.score, 0)
        self.assertEqual(game._total_score, 0)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_follow_player_winning(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_QUEEN_PROTO]*2)
        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_KING_PROTO]*2)
        game.state = GameState.PLAY
        game._kitty_player_name = 'player_1'
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_QUEEN_PROTO]*2)
        self.__playHandAndAssertSuccess(game, 'player_2', [HEART_KING_PROTO]*2)

        self.assertEqual(game._next_player_name, 'player_2')
        self.assertEqual(p1.score, 0)
        self.assertEqual(p2.score, 20)
        self.assertEqual(game._total_score, 20)

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_hand_follow_player_winning_by_trump(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_KING_PROTO]*2+[HEART_QUEEN_PROTO])
        p2 = self.__createPlayerWithHand(game, 'player_2', [SMALL_JOKER_PROTO]*2+[BIG_JOKER_PROTO])
        game.state = GameState.PLAY
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_KING_PROTO]*2)
        self.__playHandAndAssertSuccess(game, 'player_2', [SMALL_JOKER_PROTO]*2)

        self.assertEqual(game._next_player_name, 'player_2')

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_play_valid_hand_all_players_get_right_update(self) -> None:
        game = Game('player_1', '0', 0, 2)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_TWO_PROTO]*2)
        p2 = self.__createPlayerWithHand(game, 'player_2', [SPADE_TWO_PROTO]*2)
        game.state = GameState.PLAY
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_TWO_PROTO])

        game_proto = next(p2.update_stream())
        self.assertEqual(game_proto.next_turn_player_name, 'player_2')
        self.assertEqual(game_proto.players[0].current_round_trick, HandProto(cards=[HEART_TWO_PROTO]))

    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_four_players_kitty_team_winning(self) -> None:
        game = Game('player_1', '0', 0, 4)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_QUEEN_PROTO]*2)
        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_KING_PROTO]*2)
        p3 = self.__createPlayerWithHand(game, 'player_3', [SPADE_TWO_PROTO, HEART_FIVE_PROTO])
        p4 = self.__createPlayerWithHand(game, 'player_4', [SPADE_TEN_PROTO, HEART_FIVE_PROTO])
        game.state = GameState.PLAY
        game._kitty_player_name = 'player_4'
        game._next_player_name = 'player_2'

        self.__playHandAndAssertSuccess(game, 'player_2', [HEART_KING_PROTO]*2)
        self.__playHandAndAssertSuccess(game, 'player_3', [SPADE_TWO_PROTO, HEART_FIVE_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_4', [SPADE_TEN_PROTO, HEART_FIVE_PROTO])
        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_QUEEN_PROTO]*2)

        self.assertEqual(game._next_player_name, 'player_2')
        self.assertEqual(p2.score, 40)
        self.assertEqual(game._total_score, 0)


    @timeout_decorator.timeout(DEFAULT_TEST_TIMEOUT)
    def test_four_players_kitty_team_losing(self) -> None:
        game = Game('player_1', '0', 0, 4)
        p1 = self.__createPlayerWithHand(game, 'player_1', [HEART_QUEEN_PROTO]*2)
        p2 = self.__createPlayerWithHand(game, 'player_2', [HEART_KING_PROTO]*2)
        p3 = self.__createPlayerWithHand(game, 'player_3', [SPADE_TWO_PROTO]*2)
        p4 = self.__createPlayerWithHand(game, 'player_4', [SPADE_TEN_PROTO, HEART_FIVE_PROTO])
        game.state = GameState.PLAY
        game._kitty_player_name = 'player_4'
        game._next_player_name = 'player_1'

        self.__playHandAndAssertSuccess(game, 'player_1', [HEART_QUEEN_PROTO]*2)
        self.__playHandAndAssertSuccess(game, 'player_2', [HEART_KING_PROTO]*2)
        self.__playHandAndAssertSuccess(game, 'player_3', [SPADE_TWO_PROTO]*2)
        self.__playHandAndAssertSuccess(game, 'player_4', [SPADE_TEN_PROTO, HEART_FIVE_PROTO])

        self.assertEqual(game._next_player_name, 'player_3')
        self.assertEqual(p3.score, 35)
        self.assertEqual(game._total_score, 35)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configuration for unit tests.')
    parser.add_argument('--debug', metavar='d', type=bool, default=False, required=False,
                        help='If set, print spammy debug logging to sdout.')
    args = parser.parse_args()
    if args.debug == True:
        logging.basicConfig(
                stream=sys.stdout,
                level=logging.DEBUG,
                format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')
    unittest.main()
