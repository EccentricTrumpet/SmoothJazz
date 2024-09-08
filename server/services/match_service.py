from itertools import count
from typing import Dict, Iterator
from abstractions.match import Match


class MatchService:
    def __init__(self) -> None:
        # Dict that holds match states.
        self.__matches: Dict[str, Match] = dict()
        # match_id is a monotonically increasing number
        self.__match_id: Iterator[int] = count()

    def create_match(self, creator_name: str, delay: float, open_hand: bool) -> int:
        match_id = str(next(self.__match_id))
        self.__matches[match_id] = Match(
            creator_name, match_id, delay, open_hand=open_hand
        )
        return match_id
