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

global_executor = ThreadPoolExecutor()

def DealCards(game_id):
    keep_going = True
    while keep_going:
        Shengji.game_state_lock.acquire()
        keep_going = Shengji.games[game_id].DealCard()
        Shengji.game_state_lock.release()

        Shengji.NotifyGameStateChange(game_id)


class Shengji(shengji_pb2_grpc.ShengjiServicer):
    # game_state_lock protects all shared game states
    game_state_lock = threading.RLock()
    game_watchers = dict()
    games = dict()
    game_id = 0

    def __init__(self):
        pass

    @classmethod
    def NotifyGameStateChange(cls, game_id):
        logging.info("Notifying changes")
        with cls.game_watchers[game_id]:
            cls.game_watchers[game_id].notify_all()

    def CreateGame(self,
            request: shengji_pb2.CreateGameRequest,
            context: grpc.ServicerContext
            ) -> shengji_pb2.Game:
        game_id = str(self.game_id)

        self.game_state_lock.acquire()
        self.game_id += 1
        self.games[game_id] = Game(request.player_id, game_id)

        # Creates a game watcher
        self.game_watchers[game_id] = threading.Condition()
        game = self.games[game_id].ToApiGame()
        self.game_state_lock.release()

        logging.info("Received a CreateGame request from player_id [%s], created a game with id [%s]", request.player_id, game_id)
        return game


    def TerminateGame(self, game_id: str):
        logging.info("Terminating game: %s", game_id)
        del self.games[game_id]
        Shengji.NotifyGameStateChange(game_id)

    def PlayHand(self, request, context):
        self.game_state_lock.acquire()

        logging.info("Received a PlayGame request from player_id [%s], game_id [%s]", request.player_id, request.game_id)
        game_id = request.game_id
        player_id = request.player_id

        try:
            self.games[game_id]
        except:
            logging.info("Not found: game_id [%s]", request.game_id)
        game = self.games[game_id]

        self.game_state_lock.release()

        # Notifies all watchers of state change
        Shengji.NotifyGameStateChange(request.game_id)

        return game

    def _addPlayer(self, game_id, player_id):
        self.game_state_lock.acquire()
        self.games[game_id].AddPlayer(player_id)
        self.game_state_lock.release()

        Shengji.NotifyGameStateChange(game_id)

        # start the game by having an executor deal cards
        if len(self.games[game_id].player_ids) == 4:
            logging.info("Dealing cards...")
            global_executor.submit(DealCards, (game_id))


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
        self._addPlayer(request.game_id, request.player_id)

        # Send out the initial game
        self.game_state_lock.acquire()
        game = self.games[request.game_id]
        self.game_state_lock.release()
        yield game.ToApiGame()

        # wait for notification
        while request.game_id in self.games:
            with self.game_watchers[request.game_id]:
                logging.info("Player [%s] is waiting for game update [%s]", request.player_id, self.game_watchers[request.game_id])
                self.game_watchers[request.game_id].wait()

                logging.info("Player [%s] got game update", request.player_id)
                if request.game_id not in self.games:
                    break
                self.game_state_lock.acquire()
                game = self.games[request.game_id]
                self.game_state_lock.release()
            yield game.ToApiGame()

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
