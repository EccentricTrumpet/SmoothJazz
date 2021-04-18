# Copyright 2020 The gRPC Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use self file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Iterable
import threading

import grpc
from google.protobuf.json_format import MessageToJson

import shengji_pb2
import shengji_pb2_grpc

class Shengji(shengji_pb2_grpc.ShengjiServicer):
    # game_state_lock protects all shared game states
    game_state_lock = threading.RLock()
    game_watchers = dict()
    game = dict()
    game_id = 0

    def __init__(self):
        pass

    def CreateGame(self, request, context):
        self.game_state_lock.acquire()

        game_id = str(self.game_id)
        self.game[game_id] = shengji_pb2.Game() 
        self.game_id += 1
        self.game[game_id].game_id = game_id
        self.game[game_id].creator_player_id = request.player_id
        self.game[game_id].data.state = shengji_pb2.GameData.NOT_ENOUGH_PLAYERS

        # Creates a game watcher
        self.game_watchers[game_id] = threading.Condition()

        logging.info("Received a CreateGame request from player_id [%s], created a game with id [%s]", request.player_id, game_id)

        game = self.game[game_id]
        self.game_state_lock.release()
        return game

    def PlayGame(self, request, context):
        logging.info("Received a PlayGame request from player_id [%s], game_id [%s]", request.player_id, request.game_id)
        game_id = request.game_id
        player_id = request.player_id
        self.game_state_lock.acquire()

        try:
            self.game[game_id]
        except:
            logging.info("Not found: game_id [%s]", request.game_id)
        self.game[game_id].state.game_move_count += 1
        game = self.game[game_id]

        self.game_state_lock.release()

        # Notifies all watchers of state change
        with self.game_watchers[game_id]:
            self.game_watchers[game_id].notify_all()

        return game

    def _addPlayer(self, game_id, player_name):
        self.game_state_lock.acquire()
        self.game[game_id].player_ids.append(player_name)
        if len(self.game[game_id].player_ids) == 4:
            self.game[game_id].data.state = shengji_pb2.GameData.STARTED
        # Notifies all watchers of state change
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
        game = self.game[request.game_id]
        self.game_state_lock.release()
        yield game
        while True:
            with self.game_watchers[request.game_id]:
                logging.info("Waiting for game update [%s]", self.game_watchers[request.game_id])
                self.game_watchers[request.game_id].wait()
                logging.info("Streaming game update...")
                self.game_state_lock.acquire()
                game = self.game[request.game_id]
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
