import asyncio
import logging
import random
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from itertools import count
from game_state import Game
from typing import (
    Iterable,
    Dict,
    Iterator)
from shengji_pb2_grpc import (
    ShengjiServicer,
    add_ShengjiServicer_to_server)
from shengji_pb2 import (
    AddAIPlayerRequest,
    AddAIPlayerResponse,
    CreateGameRequest,
    EnterRoomRequest,
    PlayHandRequest,
    PlayHandResponse,
    Game as GameProto)
from grpc import (
    ServicerContext,
    aio)

class SJService(ShengjiServicer):
    def __init__(self, delay: float = 0.3) -> None:
        # delay for dealing cards
        self.__delay: float = delay
        # Dict that holds game states.
        self.__games: Dict[str, Game] = dict()
        # game_id is a monotonically increasing number
        self.__game_id: Iterator[int] = count()

    def CreateGame(self,
            request: CreateGameRequest,
            context: ServicerContext
            ) -> GameProto:

        logging.info(f'Received a CreateGame request from player_id: {request.player_id}')

        game_id = str(next(self.__game_id))
        game = Game(request.player_id, game_id, self.__delay)
        self.__games[game_id] = game

        logging.info(f'Created game with id: {game_id}')

        return game.ToGameProto()

    def AddAIPlayer(self,
                   request: AddAIPlayerRequest,
                   context: ServicerContext
                   ) -> AddAIPlayerResponse:
        ai_name = 'Computer' + str(random.randrange(10000))
        logging.info(f'Adding AI: {ai_name} to game: {request.game_id}')

        game = self.__getGame(request.game_id)
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
                  context: ServicerContext
                  ) -> Iterable[Game]:
        logging.info("Received a EnterRoom request: %s", request)

        game = self.__getGame(request.game_id)
        player = game.AddPlayer(request.player_id, True)

        if game.state == 'NOT_STARTED':
            thread = threading.Thread(target=game.DealCards(), args=())

        for update in player.UpdateStream():
            yield update

    def PlayHand(self,
            request: PlayHandRequest,
            context: ServicerContext) -> PlayHandResponse:
        logging.info("Received a PlayGame request [%s] from player_id [%s], game_id [%s]",
                request.hand, request.player_id, request.game_id)
        with SJService.game_state_lock:
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

    def TerminateGame(self, game_id: str) -> None:
        game = self.__getGame(game_id)
        game.CompletePlayerStreams()
        del self.__games[game_id]

    def __getGame(self, game_id: str) -> Game:
        game = self.__games.get(game_id, None)
        if game is None:
            raise RuntimeError(f'Cannot retrieve non-existent game: {game_id}')
        return game

async def serve(address: str) -> None:
    server = aio.server(ThreadPoolExecutor(max_workers=100))
    # A new executor for tasks that exist beyond RPC context. (e.g. dealing
    # cards)
    add_ShengjiServicer_to_server(SJService(), server)
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
