import asyncio
from concurrent.futures import thread
from concurrent.futures.thread import ThreadPoolExecutor
import logging
import random
import time
import threading
from typing import Iterable, Dict
from itertools import count
from shengji_pb2 import *
from shengji_pb2_grpc import *

# Import from files in directory
from game_state import *

# Import warnings
import grpc
from google.protobuf.json_format import MessageToJson

class SJServicer(ShengjiServicer):
    # Dict that holds game states.
    _games: Dict[str, SJGame] = dict()

    # game_id is a monotonically increasing number
    _game_id = count()

    def __init__(self, delay=0.3):
        self._delay = delay

    def CreateGame(self,
            request: CreateGameRequest,
            context: grpc.ServicerContext
            ) -> Game:

        logging.info(f'Received a CreateGame request from player_id: {request.player_id}')

        game_id = str(next(self._game_id))
        game = SJGame(request.player_id, game_id, self._delay)
        self._games[game_id] = game

        logging.info(f'Created game with id: {game_id}')

        return game.ToApiGame()

    def AddAIPlayer(self,
                   request: AddAIPlayerRequest,
                   context: grpc.ServicerContext
                   ) -> AddAIPlayerResponse:
        ai_name = 'Computer' + str(random.randrange(10000))
        logging.info(f'Adding AI: {ai_name} to game: {request.game_id}')

        game = self._getGame(request.game_id)
        game.AddPlayer(ai_name, False)

        if game.state == 'NOT_STARTED':
            thread = threading.Thread(target=game.DealCards(), args=())
            thread.start()

        # API: This is ignored by the frontend so is this needed?
        ai_player = AddAIPlayerResponse()
        ai_player.player_name = ai_name

        return ai_player

    def EnterRoom(self,
                  request: EnterRoomRequest,
                  context: grpc.ServicerContext
                  ) -> Iterable[Game]:
        logging.info("Received a EnterRoom request: %s", request)

        game = self._getGame(request.game_id)
        player = game.AddPlayer(request.player_id, True)

        if game.state == 'NOT_STARTED':
            thread = threading.Thread(target=game.DealCards(), args=())

        # Send out the initial game
        yield game.ToApiGame()

        for update in player.UpdateStream():
            yield update

    def PlayHand(self,
            request: PlayHandRequest,
            context: grpc.ServicerContext) -> PlayHandResponse:
        logging.info("Received a PlayGame request [%s] from player_id [%s], game_id [%s]",
                request.hand, request.player_id, request.game_id)
        with SJServicer.game_state_lock:
            game_id = request.game_id
            player_id = request.player_id

            try:
                self.games[game_id]
            except:
                logging.info("Not found: game_id [%s]", request.game_id)
            # TODO: Play card and notify all players
            # game = self.games[game_id]

        # Notifies all watchers of state change
        return PlayHandResponse()

    def TerminateGame(self, game_id):
        game = self._getGame(game_id)
        game.CompletePlayerStreams()
        del self._games[game_id]

    def _getGame(self, game_id) -> SJGame:
        game = self._games.get(game_id, None)
        if game is None:
            raise RuntimeError(f'Cannot retrieve non-existent game: {game_id}')
        return game

async def serve(address: str):
    server = grpc.aio.server(ThreadPoolExecutor(max_workers=100))
    # A new executor for tasks that exist beyond RPC context. (e.g. dealing
    # cards)
    add_ShengjiServicer_to_server(SJServicer(), server)
    server.add_insecure_port(address)
    await server.start()
    logging.info("Server serving at %s", address)
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
            format="%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s")
    asyncio.run(serve("[::]:50051"))
