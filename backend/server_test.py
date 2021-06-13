import unittest
import logging
import sys
import time
from concurrent import futures
from server import SJService
from shengji_pb2 import (
    AddAIPlayerRequest,
    CreateGameRequest,
    DrawCardsRequest,
    EnterRoomRequest)

# TODO(aaron): Add unit tests for 4 real players
class ShengjiTest(unittest.TestCase):

    def test_create_game(self) -> None:
        sj = SJService(delay=0)
        req = CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.createGame(req, None)
        self.assertEqual(game.creator_player_id, req.player_id)

    # A wrapper that returns the generator items as a list so that
    # it can work with concurrent.future for async execution.
    def __generator_wrap(self, functor, *args):
        return list(functor(*args))

    def test_streaming_with_one_ai(self) -> None:
        sj = SJService(delay=0)
        req = CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.createGame(req, None)

        enter_room_req = EnterRoomRequest()
        enter_room_req.game_id = game.game_id
        enter_room_req.player_id = req.player_id

        with futures.ThreadPoolExecutor(max_workers=1) as pool:
            f = pool.submit(self.__generator_wrap, sj.enterRoom, enter_room_req, None)
            add_ai_req = AddAIPlayerRequest()
            add_ai_req.game_id = game.game_id
            sj.addAIPlayer(add_ai_req, None)
            # Sleep for half a second so that creator can get the updates.
            time.sleep(0.5)
            sj.terminate_game(game.game_id)

            streaming_result = f.result()

            self.assertEqual(streaming_result[-1].game_id, game.game_id)
            self.assertEqual(streaming_result[-1].creator_player_id, req.player_id)
            self.assertEqual(len(streaming_result[-1].players), 2)

    def test_deal_cards(self) -> None:
        sj = SJService(delay=0)
        req = CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.createGame(req, None)

        enter_room_req = EnterRoomRequest()
        enter_room_req.game_id = game.game_id
        enter_room_req.player_id = req.player_id

        draw_req = DrawCardsRequest()
        draw_req.game_id = game.game_id
        draw_req.player_name = req.player_id

        with futures.ThreadPoolExecutor(max_workers=2) as pool:
            add_ai_req = AddAIPlayerRequest()
            add_ai_req.game_id = game.game_id

            # Add three AI players
            sj.addAIPlayer(add_ai_req, None)
            sj.addAIPlayer(add_ai_req, None)
            sj.addAIPlayer(add_ai_req, None)

            # Add the human player last (so we can trigger card dealing)
            f = pool.submit(self.__generator_wrap, sj.enterRoom, enter_room_req, None)

            # Draw hands
            sj.drawCards(draw_req, None)

            # Draw kitty
            sj.drawCards(draw_req, None)

            time.sleep(1.0)
            sj.terminate_game(game.game_id)

            streaming_result = f.result()

            self.assertEqual(streaming_result[1].game_id, game.game_id)
            self.assertEqual(streaming_result[1].creator_player_id, req.player_id)

            self.assertEqual(len(streaming_result[-1].players), 4)
            self.assertEqual(len(streaming_result[-1].players[0].cards_on_hand.cards), 25)
            self.assertEqual(len(streaming_result[-1].players[3].cards_on_hand.cards), 33)

            # Expected number of game state updates is
            # 1 for human player joining game
            # 100 for dealing cards
            # 8 for dealing kitty
            self.assertEqual(len(streaming_result), 109)

if __name__ == '__main__':
    logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s")
    unittest.main()
