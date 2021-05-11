import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable
import threading

import grpc
from google.protobuf.json_format import MessageToJson

import shengji_pb2
import shengji_pb2_grpc
from game_state import *

class Shengji(shengji_pb2_grpc.ShengjiServicer):
    # game_state_lock protects all shared game states
    game_state_lock = threading.RLock()
    game_watchers = dict()
    games = dict()
    game_id = 0

    def __init__(self):
        pass

    def CreateGame(self,
            request: shengji_pb2.CreateGameRequest,
            context: grpc.ServicerContext
            ) -> shengji_pb2.Game:
        self.game_state_lock.acquire()

        game_id = str(self.game_id)
        self.games[game_id] = shengji_pb2.Game() 
        self.game_id += 1
        self.games[game_id].game_id = game_id
        self.games[game_id].creator_player_id = request.player_id

        # Creates a game watcher
        self.game_watchers[game_id] = threading.Condition()

        logging.info("Received a CreateGame request from player_id [%s], created a game with id [%s]", request.player_id, game_id)

        game = self.games[game_id]
        self.game_state_lock.release()
        return game

    def TerminateGame(self, game_id: str):
        logging.info("Terminating game: %s", game_id)
        del self.games[game_id]
        with self.game_watchers[game_id]:
            self.game_watchers[game_id].notify_all()

    def PlayHand(self, request, context):
        logging.info("Received a PlayGame request from player_id [%s], game_id [%s]", request.player_id, request.game_id)
        logging.info("UNIMPLEMENTED")
        game_id = request.game_id
        player_id = request.player_id
        self.game_state_lock.acquire()

        try:
            self.games[game_id]
        except:
            logging.info("Not found: game_id [%s]", request.game_id)
        game = self.games[game_id]

        self.game_state_lock.release()

        # Notifies all watchers of state change
        with self.game_watchers[game_id]:
            self.game_watchers[game_id].notify_all()

        return game

    def _addPlayer(self, game_id, player_id):
        self.game_state_lock.acquire()
        player_state = shengji_pb2.PlayerState()
        player_state.player_id = player_id 
        self.games[game_id].player_states.append(player_state)
        with self.game_watchers[game_id]:
            self.game_watchers[game_id].notify_all()
        self.game_state_lock.release()

    def AddAIPlayer(self,
                   request: shengji_pb2.AddAIPlayerRequest,
                   context: grpc.ServicerContext
                   ) -> shengji_pb2.AddAIPlayerResponse:
        logging.info("Adding AI to game: %s", request.game_id)
        ai_name = "alex"
        self._addPlayer(request.game_id, ai_name)
        ai_player= shengji_pb2.AddAIPlayerResponse()
        ai_player.player_name = ai_name
        return ai_player

    def EnterRoom(self,
                   request: shengji_pb2.EnterRoomRequest,
                   context: grpc.ServicerContext
                  ) -> Iterable[shengji_pb2.Game]:
        logging.info("Received a EnterRoom request: %s", request)
        self._addPlayer(request.game_id, request.player_id)

        # wait for notification
        with self.game_watchers[request.game_id]:
            self.game_watchers[request.game_id].notify_all()
        self.game_state_lock.acquire()
        game = self.games[request.game_id]
        self.game_state_lock.release()
        yield game

        while request.game_id in self.games:
            with self.game_watchers[request.game_id]:
                logging.info("Waiting for game update [%s]", self.game_watchers[request.game_id])
                self.game_watchers[request.game_id].wait()
                logging.info("Streaming game update...")
                if request.game_id not in self.games:
                    break
                self.game_state_lock.acquire()
                game = self.games[request.game_id]
                self.game_state_lock.release()
            yield game

        logging.info("Call finished [%s]", request.game_id)


def serve(address: str) -> None:
    server = grpc.server(ThreadPoolExecutor())
    shengji_pb2_grpc.add_ShengjiServicer_to_server(Shengji(), server)
    server.add_insecure_port(address)
    server.start()
    logging.info("Server serving at %s", address)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s")
    serve("[::]:50051")
