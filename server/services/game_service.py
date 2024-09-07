from itertools import count
from typing import Dict, Iterator
from abstractions.game import Game


class GameService:
    def __init__(self) -> None:
        # Dict that holds game states.
        self.__games: Dict[str, Game] = dict()
        # game_id is a monotonically increasing number
        self.__game_id: Iterator[int] = count()

    def create_game(self) -> int:
        game_id = str(next(self.__game_id))
        self.__games[game_id] = Game()
        return game_id
