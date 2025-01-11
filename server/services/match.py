from itertools import count
from typing import Callable, Dict, Iterator

from abstractions import PlayerError, Room, Room_
from abstractions.events import CardsEvent, JoinEvent, PlayerEvent
from abstractions.responses import MatchResponse
from core.match import Match


class MatchService:
    def __init__(self) -> None:
        # Monotonically increasing ids
        self.__match_id: Iterator[int] = count()
        self.__matches: Dict[int, Match] = dict()

    def __try[T](self, event: T, room: Room, func: Callable[[T, Room], None]) -> Room_:
        try:
            func(event, room)
        except PlayerError as error:
            room.reply("error", error)
        return room

    def __invoke[
        T: (PlayerEvent, CardsEvent)
    ](self, event: T, func: Callable[[Match], Callable[[T, Room], None]]) -> Room_:
        if event.match_id not in self.__matches:
            return None

        match = self.__matches[event.match_id]
        player = next((p for p in match.players if p.id == event.pid), None)

        if player is not None:
            return self.__try(event, Room(event.match_id, event.sid), func(match))

    def create(self, debug: bool) -> MatchResponse:
        match_id = next(self.__match_id)
        new_match = Match(match_id, debug)
        self.__matches[match_id] = new_match
        return new_match.response()

    def get(self, match_id: int) -> MatchResponse | None:
        if match_id in self.__matches:
            return self.__matches[match_id].response()

    def join(self, event: JoinEvent) -> Room_:
        if event.match_id in self.__matches:
            room = Room(event.match_id, event.sid)
            return self.__try(event, room, self.__matches[event.match_id].join)

    def leave(self, event: PlayerEvent) -> Room_:
        return self.__invoke(event, lambda match: match.join)

    def draw(self, event: PlayerEvent) -> Room_:
        return self.__invoke(event, lambda match: match.draw)

    def bid(self, event: CardsEvent) -> Room_:
        return self.__invoke(event, lambda match: match.bid)

    def kitty(self, event: CardsEvent) -> Room_:
        return self.__invoke(event, lambda match: match.kitty)

    def play(self, event: CardsEvent) -> Room_:
        return self.__invoke(event, lambda match: match.play)

    def next(self, event: PlayerEvent) -> Room_:
        return self.__invoke(event, lambda match: match.next)
