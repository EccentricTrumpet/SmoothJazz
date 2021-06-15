import unittest
import logging
import sys
import timeout_decorator
from game_state import GameState
from server import SJService
from shengji_pb2 import (
    AddAIPlayerRequest,
    CreateGameRequest,
    DrawCardsRequest,
    JoinGameRequest)

# TODO(aaron): Add unit tests for 4 real players
class ShengjiTest(unittest.TestCase):

    @timeout_decorator.timeout(5)
    def test_create_game(self) -> None:
        sj = SJService(delay=0)
        req = CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.createGame(req, None)
        self.assertEqual(game.game_id, str(0))

    @timeout_decorator.timeout(5)
    def test_streaming_with_three_ais(self) -> None:
        sj = SJService(delay=0)
        req = CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.createGame(req, None)

        join_game_req = JoinGameRequest()
        join_game_req.game_id = game.game_id
        join_game_req.player_id = req.player_id

        updates = sj.joinGame(join_game_req, None)
        # Need to trigger the iterable to invoke the method
        streaming_result = [next(updates)]

        # Add three AI players
        add_ai_req = AddAIPlayerRequest()
        add_ai_req.game_id = game.game_id

        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)

        for update in updates:
            streaming_result.append(update)
            if update.next_turn_player_id == GameState.AWAIT_DEAL.name:
                break

        sj.terminate_game(game.game_id)

        self.assertEqual(streaming_result[-1].game_id, game.game_id)
        self.assertEqual(streaming_result[-1].creator_player_id, req.player_id)
        self.assertEqual(len(streaming_result[-1].players), 4)

    @timeout_decorator.timeout(5)
    def test_deal_cards(self) -> None:
        sj = SJService(delay=0)
        req = CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.createGame(req, None)

        add_ai_req = AddAIPlayerRequest()
        add_ai_req.game_id = game.game_id

        # Add three AI players
        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)

        join_game_req = JoinGameRequest()
        join_game_req.game_id = game.game_id
        join_game_req.player_id = req.player_id

        updates = sj.joinGame(join_game_req, None)
        # Need to trigger the iterable to invoke the method
        streaming_result = [next(updates)]

        draw_req = DrawCardsRequest()
        draw_req.game_id = game.game_id
        draw_req.player_name = req.player_id

        # Draw hands
        sj.drawCards(draw_req, None)

        # Draw kitty
        sj.drawCards(draw_req, None)

        for update in updates:
            streaming_result.append(update)
            if update.next_turn_player_id == GameState.HIDE_KITTY.name:
                break

        # Terminate game
        sj.terminate_game(game.game_id)

        # Expected number of game state updates is
        # 1 for human player joining game
        # 100 for dealing cards
        # 8 for dealing kitty
        self.assertEqual(len(streaming_result), 109)

        self.assertEqual(streaming_result[0].game_id, game.game_id)
        self.assertEqual(streaming_result[0].creator_player_id, req.player_id)

        self.assertEqual(len(streaming_result[-1].players), 4)
        self.assertEqual(len(streaming_result[-1].players[0].cards_on_hand.cards), 25)
        self.assertEqual(len(streaming_result[-1].players[3].cards_on_hand.cards), 33)

if __name__ == '__main__':
    logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s")
    unittest.main()
