import asyncio
import logging
import random
import threading
from concurrent.futures.thread import ThreadPoolExecutor
from grpc import ServicerContext
from grpc.aio import server as GrpcServer
from itertools import count
from game_state import (
    Card,
    Game,
    GameState)
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

class SJService(ShengjiServicer):
    def __init__(self, delay: float = 0.3) -> None:
        # delay for dealing cards
        self.__delay: float = delay
        # Dict that holds game states.
        self.__games: Dict[str, Game] = dict()
        # game_id is a monotonically increasing number
        self.__game_id: Iterator[int] = count()

    def createGame(self,
            request: CreateGameRequest,
            context: ServicerContext
            ) -> GameProto:

        logging.info(f'Received a CreateGame request from player_id: {request.player_id}')

        game_id = str(next(self.__game_id))
        game = Game(request.player_id, game_id, self.__delay)
        self.__games[game_id] = game

        logging.info(f'Created game with id: {game_id}')

        game_proto = game.to_game_proto(False)
        game_proto.new_player_update.player_id = request.player_id

        return game_proto

    def addAIPlayer(self,
                   request: AddAIPlayerRequest,
                   context: ServicerContext
                   ) -> AddAIPlayerResponse:
        ai_name = f'Computer{random.randrange(10000)}'
        logging.info(f'Adding AI: {ai_name} to game: {request.game_id}')

        game = self.__get_game(request.game_id)
        game.add_player(ai_name, False)

        if game.state == GameState.AWAIT_DEAL:
            thread = threading.Thread(target=game.deal_cards(), args=())
            thread.start()

        # API: This is ignored by the frontend so is this needed?
        ai_player = AddAIPlayerResponse()
        ai_player.player_name = ai_name

        return ai_player

    def enterRoom(self,
                  request: EnterRoomRequest,
                  context: ServicerContext
                  ) -> Iterable[Game]:
        logging.info(f'Received a EnterRoom request: {request}')

        game = self.__get_game(request.game_id)
        player = game.add_player(request.player_id, True)

        if game.state == GameState.AWAIT_DEAL:
            thread = threading.Thread(target=game.deal_cards(), args=())
            thread.start()

        for update in player.update_stream():
            yield update

    def playHand(self,
            request: PlayHandRequest,
            context: ServicerContext) -> PlayHandResponse:
        logging.info(f'Received a playHand request [{request.hand}] from player_id [{request.player_id}], game_id [{request.game_id}]')

        try:
            game = self.__games[request.game_id]
        except:
            logging.info(f'Not found: game_id [{request.game_id}]')
            response = PlayHandResponse()
            response.success = False
            response.error_message = f'Game {request.game_id} does not exist'
            return response

        (success, error_message) = game.play(request.player_id, [Card.from_card_proto(c) for c in request.hand.cards])

        response = PlayHandResponse()
        response.success = success
        response.error_message = error_message

        return response

    def terminate_game(self, game_id: str) -> None:
        game = self.__get_game(game_id)
        game.complete_player_stream()
        del self.__games[game_id]

    def __get_game(self, game_id: str) -> Game:
        game = self.__games.get(game_id, None)
        if game is None:
            raise RuntimeError(f'Cannot retrieve non-existent game: {game_id}')
        return game

async def serve(address: str) -> None:
    server = GrpcServer(ThreadPoolExecutor(max_workers=100))
    # A new executor for tasks that exist beyond RPC context. (e.g. dealing
    # cards)
    add_ShengjiServicer_to_server(SJService(), server)
    server.add_insecure_port(address)
    await server.start()
    logging.info(f'Server serving at {address}')
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        # Shuts down the server with 0 seconds of grace period. During the
        # grace period, the server won't accept new connections and allow
        # existing RPCs to continue within the grace period.
        await server.stop(0)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
            format='%(asctime)s [%(levelname)s] [%(threadName)s]: %(message)s')
    asyncio.run(serve('[::]:50051'))
