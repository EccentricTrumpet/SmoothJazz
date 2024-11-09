from core.format import Format
from abstractions.requests import PlayRequest


class Trick:
    def __init__(self, num_players) -> None:
        self.__num_players = num_players
        self.__plays: dict[int, Format] = {}
        self.score = 0
        self.winner_id = -1

    def play(self, request: PlayRequest) -> bool:
        # Mock logic
        if self.winner_id == -1:
            self.winner_id = request.player_id
        self.__plays[request.player_id] = Format()
        self.score += 5
        return True

    def is_done(self) -> bool:
        return len(self.__plays) == self.__num_players
