from ai import AaronAI
import argparse
import asyncio
import threading
import logging
import random
from concurrent.futures.thread import ThreadPoolExecutor
from grpc import ServicerContext
from grpc.aio import server as GrpcServer
from itertools import count
from game_state import (
    Game)
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
    CreateGameResponse,
    DrawCardsRequest,
    JoinGameRequest,
    DrawCardsResponse,
    PlayHandRequest,
    PlayHandResponse,
    Game as GameProto)


class SJService(ShengjiServicer):
    def __init__(self) -> None:
        # Dict that holds game states.
        self.__games: Dict[str, Game] = dict()
        # game_id is a monotonically increasing number
        self.__game_id: Iterator[int] = count()

    def createGame(self,
            request: CreateGameRequest,
            context: ServicerContext
            ) -> GameProto:

        logging.info(f'Received a CreateGame request from player_name: {request.player_name}')

        game_id = str(next(self.__game_id))
        self.__games[game_id] = Game(request.player_name, game_id, 0.5 / request.game_speed)

        logging.info(f'Created game with id: {game_id}')
        return CreateGameResponse(game_id=game_id)

    def addAIPlayer(self,
                   request: AddAIPlayerRequest,
                   context: ServicerContext
                   ) -> AddAIPlayerResponse:
        ai_name = f'Computer{random.randrange(10000)}'
        logging.info(f'Adding AI: {ai_name} to game: {request.game_id}')

        game = self.__get_game(request.game_id)
        player = game.add_player(ai_name, True)

        if request.ai_type == AddAIPlayerRequest.AARON_AI:
            my_ai = AaronAI(game, player, game.get_game_delay())
            threading.Thread(target=my_ai.start, daemon=True).start()

        logging.info(f'Returning AddAIPlayerRequest for {ai_name}')

        return AddAIPlayerResponse(player_name=ai_name)

    def joinGame(self,
                  request: JoinGameRequest,
                  context: ServicerContext
                  ) -> Iterable[Game]:
        logging.info(f'Received a JoinGame request: {request.player_name} wants to join game {request.game_id}')

        game = self.__get_game(request.game_id)
        player = game.add_player(request.player_name, True)

        for update in player.update_stream():
            yield update

    def playHand(self,
            request: PlayHandRequest,
            context: ServicerContext) -> PlayHandResponse:
        logging.info(f'Received a playHand request [{request.hand}] from player_name [{request.player_name}], game_id [{request.game_id}]')

        try:
            game = self.__get_game(request.game_id)
        except:
            response = PlayHandResponse()
            response.success = False
            response.error_message = f'Game {request.game_id} does not exist'
            return response

        (success, error_message) = game.play(request.player_name, request.hand.cards)

        response = PlayHandResponse()
        response.success = success
        response.error_message = error_message

        return response

    def drawCards(self,
        request: DrawCardsRequest,
        context: ServicerContext) -> DrawCardsResponse:

        game = self.__get_game(request.game_id)
        game.draw_cards(request.player_name)

        return DrawCardsResponse()

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
            format='%(asctime)s [%(levelname)s] [%(threadName)s] {%(filename)s:%(lineno)d}: %(message)s')

    parser = argparse.ArgumentParser(description='Configuration for server.')
    parser.add_argument('--debug', metavar='d', type=bool, default=False, required=False,
                        help='If set, print spammy debug logging.')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s [%(levelname)s] [%(threadName)s] {%(filename)s:%(lineno)d}: %(message)s')
    asyncio.run(serve('[::]:50051'))
