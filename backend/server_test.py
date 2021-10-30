import unittest
import logging
import sys
import timeout_decorator
from server import SJService
from shengji_pb2 import (
    AddAIPlayerRequest,
    CreateGameRequest,
    DrawCardsRequest,
    JoinGameRequest,
    Game as GameProto)

# TODO(aaron): Add unit tests for 4 real players
class ShengjiTest(unittest.TestCase):

    @timeout_decorator.timeout(20)
    def test_create_game(self) -> None:
        sj = SJService()
        req = CreateGameRequest()
        req.player_name = "test_creation_id"
        req.game_speed = 1000
        game = sj.createGame(req, None)
        self.assertEqual(game.game_id, str(0))

    @timeout_decorator.timeout(20)
    def test_streaming_with_three_ais(self) -> None:
        sj = SJService()
        req = CreateGameRequest()
        req.player_name = "test_creation_id"
        req.game_speed = 1000
        game = sj.createGame(req, None)

        join_game_req = JoinGameRequest()
        join_game_req.game_id = game.game_id
        join_game_req.player_name = req.player_name

        updates = sj.joinGame(join_game_req, None)
        # Need to trigger the iterable to invoke the method
        streaming_result = [next(updates)]

        # Add three AI players
        add_ai_req = AddAIPlayerRequest(
            game_id=game.game_id, ai_type=AddAIPlayerRequest.AIType.NONE)

        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)

        for update in updates:
            streaming_result.append(update)
            if update.state == GameProto.GameState.AWAIT_DEAL:
                break

        sj.terminate_game(game.game_id)

        self.assertEqual(streaming_result[-1].game_id, game.game_id)
        self.assertEqual(streaming_result[-1].creator_player_name, req.player_name)
        self.assertEqual(len(streaming_result[-1].players), 4)

    @timeout_decorator.timeout(20)
    def test_deal_cards(self) -> None:
        sj = SJService()
        req = CreateGameRequest()
        req.player_name = "test_creation_id"
        req.game_speed = 1000
        game = sj.createGame(req, None)

        add_ai_req = AddAIPlayerRequest(
            game_id=game.game_id, ai_type=AddAIPlayerRequest.AIType.NONE)

        # Add three AI players
        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)
        sj.addAIPlayer(add_ai_req, None)

        join_game_req = JoinGameRequest()
        join_game_req.game_id = game.game_id
        join_game_req.player_name = req.player_name

        updates = sj.joinGame(join_game_req, None)
        # Need to trigger the iterable to invoke the method
        streaming_result = [next(updates)]

        draw_req = DrawCardsRequest()
        draw_req.game_id = game.game_id
        draw_req.player_name = req.player_name

        # Draw hands
        sj.drawCards(draw_req, None)

        # Draw kitty
        sj.drawCards(draw_req, None)

        for update in updates:
            streaming_result.append(update)
            if update.state == GameProto.GameState.HIDE_KITTY:
                break

        # Terminate game
        sj.terminate_game(game.game_id)

        # Expected number of game state updates is
        # 1 for human player joining game
        # 100 for dealing cards
        # 8 for dealing kitty
        self.assertEqual(len(streaming_result), 109)

        self.assertEqual(streaming_result[0].game_id, game.game_id)
        self.assertEqual(streaming_result[0].creator_player_name, req.player_name)

        self.assertEqual(len(streaming_result[-1].players), 4)
        self.assertEqual(len(streaming_result[-1].players[0].cards_on_hand.cards), 25)
        self.assertEqual(len(streaming_result[-1].players[3].cards_on_hand.cards), 33)

if __name__ == '__main__':
    logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format='%(asctime)s [%(levelname)s] [%(threadName)s] {%(filename)s:%(lineno)d}: %(message)s')
    unittest.main()
