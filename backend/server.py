import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable
import threading

import grpc
from google.protobuf.json_format import MessageToJson

import shengji_pb2
import shengji_pb2_grpc
from game_state import *

from multiqueue import MultiQueue

def DealCards(game_id):
    keep_going = True
    while True:
        with Shengji.game_state_lock:
            keep_going = Shengji.games[game_id].DealCard()
            if not keep_going:
                break
            Shengji.NotifyGameStateChange(game_id)


class Shengji(shengji_pb2_grpc.ShengjiServicer):
    # game_state_lock protects all shared game states
    game_state_lock = threading.RLock()

    # game_update_queues is a dict where
    # KEY: game_id
    # VAL: a mult-consumer game update queue
    game_update_queues = dict()

    # Dict that holds game states. game_state_lock must be held prior accessing
    # this dict.
    # KEY: game_id
    # VAL: game object
    games = dict()

    # game_id is a monoincrease number
    game_id = 0
    global_executor = ThreadPoolExecutor()


    def __init__(self):
        pass

    # Notifies that game state has changed. 
    # game_state_lock must be held before entering this method
    @classmethod
    def NotifyGameStateChange(cls, game_id):
        logging.info("Notifying changes to game %s" % game_id)
        Shengji.game_update_queues[game_id].Put(Shengji.games[game_id].ToApiGame())

    def CreateGame(self,
            request: shengji_pb2.CreateGameRequest,
            context: grpc.ServicerContext
            ) -> shengji_pb2.Game:

        game_id = str(Shengji.game_id)

        with Shengji.game_state_lock:
            Shengji.game_id += 1
            Shengji.games[game_id] = Game(request.player_id, game_id)

            Shengji.game_update_queues[game_id] = MultiQueue()
            game = Shengji.games[game_id].ToApiGame()

        logging.info("Received a CreateGame request from player_id [%s], created a game with id [%s]", request.player_id, game_id)
        return game


    def TerminateGame(self, game_id: str):
        with Shengji.game_state_lock:
            # First wait until all consumers have consumed all updates
            logging.info("Terminating game %s: waiting for consumers to finish eating", game_id)
            Shengji.game_update_queues[game_id].Join()
            del Shengji.games[game_id]

    def PlayHand(self, request, context):
        logging.info("Received a PlayGame request from player_id [%s], game_id [%s]", request.player_id, request.game_id)
        with Shengji.game_state_lock:
            game_id = request.game_id
            player_id = request.player_id

            try:
                self.games[game_id]
            except:
                logging.info("Not found: game_id [%s]", request.game_id)
            game = self.games[game_id]

            # Notifies all watchers of state change
            Shengji.NotifyGameStateChange(request.game_id)

        return game

    def _addPlayer(self, game_id, player_id):
        with Shengji.game_state_lock:
            Shengji.games[game_id].AddPlayer(player_id)
            Shengji.NotifyGameStateChange(game_id)

        # start the game by having an executor deal cards
        if len(Shengji.games[game_id].player_ids) == 4:
            logging.info("Dealing cards...")
            Shengji.global_executor.submit(DealCards, (game_id))


    def AddAIPlayer(self,
                   request: shengji_pb2.AddAIPlayerRequest,
                   context: grpc.ServicerContext
                   ) -> shengji_pb2.AddAIPlayerResponse:
        ai_name = "alex" + str(random.randrange(10000))
        logging.info("Adding AI (%s) to game: %s", ai_name, request.game_id)
        self._addPlayer(request.game_id, ai_name)
        ai_player = shengji_pb2.AddAIPlayerResponse()
        ai_player.player_name = ai_name
        return ai_player

    def EnterRoom(self,
                   request: shengji_pb2.EnterRoomRequest,
                   context: grpc.ServicerContext
                  ) -> Iterable[shengji_pb2.Game]:
        logging.info("Received a EnterRoom request: %s", request)
        subscriber_id = None
        multiqueue = None
        with Shengji.game_state_lock:
            multiqueue = Shengji.game_update_queues[request.game_id]
            subscriber_id = multiqueue.Subscribe()
        self._addPlayer(request.game_id, request.player_id)

        # wait for notification
        while True:
            game = multiqueue.Poll(subscriber_id)
            if game is None:
                break
            logging.info("Player [%s] got game update", request.player_id)
            yield game

        logging.info("Call finished [%s]", request.game_id)


def serve(address: str) -> None:
    server = grpc.server(ThreadPoolExecutor())
    # A new executor for tasks that exist beyond RPC context. (e.g. dealing
    # cards)
    shengji_pb2_grpc.add_ShengjiServicer_to_server(Shengji(), server)
    server.add_insecure_port(address)
    server.start()
    logging.info("Server serving at %s", address)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s")
    serve("[::]:50051")
