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
import time
import threading
from typing import Iterator
from concurrent.futures import ThreadPoolExecutor

import grpc

import shengji_pb2
import shengji_pb2_grpc


class GamePlayer:

    def __init__(self, channel: grpc.Channel, player_id: str, game_id: str) -> None:
        self._channel = channel
        self._stub = shengji_pb2_grpc.ShengjiStub(self._channel)
        self._player_id = player_id
        self._game_id = game_id

    def play(self) -> None:
        request = shengji_pb2.PlayGameRequest()
        request.player_id = self._player_id
        request.game_id = self._game_id

        response = self._stub.PlayGame(request)
        logging.info("Played game: game[%s]", response)


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        player = GamePlayer(channel, "zexuan", "0")

        for i in range(100):
            time.sleep(1)
            player.play()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()