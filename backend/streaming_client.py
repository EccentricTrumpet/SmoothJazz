# Copyright 2020 The gRPC Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
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
import threading
from typing import Iterator
from concurrent.futures import ThreadPoolExecutor

import grpc

import shengji_pb2
import shengji_pb2_grpc


class GameMonitor:

    def __init__(self, executor: ThreadPoolExecutor, channel: grpc.Channel,
                 player_id: str) -> None:
        self._executor = executor
        self._channel = channel
        self._stub = shengji_pb2_grpc.ShengjiStub(self._channel)
        self._player_id = player_id
        self._peer_responded = threading.Event()
        self._call_finished = threading.Event()
        self._consumer_future = None

    def _response_watcher(
            self,
            response_iterator: Iterator[shengji_pb2.Game]) -> None:
        for response in response_iterator:
            # NOTE: All fields in Proto3 are optional. This is the recommended way
            # to check if a field is present or not, or to exam which one-of field is
            # fulfilled by this message.
            self._on_game_state_update(response)
        self._peer_responded.set()

    def _on_game_state_update(self, response: shengji_pb2.Game) -> None:
        logging.info("Updated game state: gamee[%s]", response)


    def call(self) -> None:
        # first create a game
        create_request = shengji_pb2.CreateGameRequest()
        create_request.player_id = self._player_id
        create_response = self._stub.createGame(create_request)
        logging.info("Created game: game_id [%s] creator_id [%s]", create_response.game_id, create_response.creator_player_id)
        self._game_id = create_response.game_id

        logging.info("Listening for game updates")
        request = shengji_pb2.EnterRoomRequest()
        request.game_id = self._game_id
        response_iterator = self._stub.EnterRoom(request)
        # Instead of consuming the response on current thread, spawn a consumption thread.
        self._consumer_future = self._executor.submit(self._response_watcher,
                                                      response_iterator)

    def wait(self) -> None:
        self._peer_responded.wait(timeout=None)
        if self._consumer_future.done():
            # If the future raises, forwards the exception here
            self._consumer_future.result()
        return True

def process_call(executor: ThreadPoolExecutor, channel: grpc.Channel,
                 player_id: str) -> None:
    game_monitor = GameMonitor(executor, channel, player_id)
    game_monitor.call()
    if game_monitor.wait():
        logging.info("Call finished!")
    else:
        logging.info("Call failed: peer didn't answer")


def run():
    executor = ThreadPoolExecutor()
    with grpc.insecure_channel("localhost:50051") as channel:
        future = executor.submit(process_call, executor, channel, "yimingk")
        future.result()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()
