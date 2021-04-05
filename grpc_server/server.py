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
        self.game[game_id].creator_user_id = request.user_id

        # Creates a game watcher
        self.game_watchers[game_id] = threading.Condition()

        logging.info("Received a CreateGame request from user_id [%s], created a game with id [%s]", request.user_id, game_id)

        game = self.game[game_id]
        self.game_state_lock.release()
        return game

    def PlayGame(self, request, context):
        logging.info("Received a PlayGame request from user_id [%s], game_id [%s]", request.user_id, request.game_id)
        game_id = request.game_id
        user_id = request.user_id
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

    def StreamGame(self,
                   request: shengji_pb2.StreamGameRequest,
                   context: grpc.ServicerContext
                  ) -> Iterable[shengji_pb2.Game]:
        logging.info("Received a StreamGame request for id [%s]", request.game_id)
        game = self.game[request.game_id]

        # wait for notification
        with self.game_watchers[request.game_id]:
            while True:
                logging.info("Waiting for game update [%s]", self.game_watchers[request.game_id])
                self.game_watchers[request.game_id].wait()
                self.game_state_lock.acquire()
                game = self.game[request.game_id]
                self.game_state_lock.release()
                logging.info("Streaming game update...")
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
    logging.basicConfig(level=logging.INFO)
    serve("[::]:50051")
