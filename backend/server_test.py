from concurrent import futures
from server import *
import shengji_pb2
import unittest
import logging
import sys
import time

# TODO(aaron): Add unit tests for 4 real players
class ShengjiTest(unittest.TestCase):

    def test_create_game(self):
        sj = Shengji()
        req = shengji_pb2.CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.CreateGame(req, None)
        self.assertEqual(game.creator_player_id, req.player_id)

    # A wrapper that returns the generator items as a list so that
    # it can work with concurrent.future for async execution.
    def _generator_wrap(self, functor, *args):
        return list(functor(*args))

    def test_streaming_with_one_ai(self):
        sj = Shengji()
        req = shengji_pb2.CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.CreateGame(req, None)

        enter_room_req = shengji_pb2.EnterRoomRequest()
        enter_room_req.game_id = game.game_id
        enter_room_req.player_id = req.player_id

        with futures.ThreadPoolExecutor(max_workers=1) as pool:
            f = pool.submit(self._generator_wrap, sj.EnterRoom, enter_room_req, None)
            add_ai_req = shengji_pb2.AddAIPlayerRequest()
            add_ai_req.game_id = game.game_id
            sj.AddAIPlayer(add_ai_req, None)
            # Sleep for half a second so that creator can get the updates.
            time.sleep(0.5)
            sj.TerminateGame(game.game_id)

            streaming_result = f.result()

            self.assertEqual(streaming_result[-1].game_id, game.game_id)
            self.assertEqual(streaming_result[-1].creator_player_id, req.player_id)
            self.assertEqual(len(streaming_result[-1].player_states), 2)

    
    def test_deal_cards(self):
        sj = Shengji()
        req = shengji_pb2.CreateGameRequest()
        req.player_id = "test_creation_id"
        game = sj.CreateGame(req, None)

        enter_room_req = shengji_pb2.EnterRoomRequest()
        enter_room_req.game_id = game.game_id
        enter_room_req.player_id = req.player_id

        with futures.ThreadPoolExecutor(max_workers=1) as pool:
            add_ai_req = shengji_pb2.AddAIPlayerRequest()
            add_ai_req.game_id = game.game_id

            # Add the human player last (so we can trigger card dealing)
            f = pool.submit(self._generator_wrap, sj.EnterRoom, enter_room_req, None)

            # Add three AI players
            sj.AddAIPlayer(add_ai_req, None)
            sj.AddAIPlayer(add_ai_req, None)
            sj.AddAIPlayer(add_ai_req, None)

            # Sleep 3 secs to deal cards
            time.sleep(3)
            sj.TerminateGame(game.game_id)

            streaming_result = f.result()

            self.assertEqual(streaming_result[1].game_id, game.game_id)
            self.assertEqual(streaming_result[1].creator_player_id, req.player_id)

            self.assertEqual(len(streaming_result[-1].player_states), 4)
            self.assertEqual(len(streaming_result[-1].player_states[0].cards_on_hand.cards), 25)

if __name__ == '__main__':
    logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s")
    unittest.main()
