from itertools import count
from typing import Callable, Iterator

from abstractions import CardsEvent, Event, JoinEvent, PlayerError, PlayerEvent, Room
from core.match import Match, MatchResponse


class MatchService:
    type EventCall[T: Event] = Callable[[T, Room], None]
    type Room_ = Room | None

    def __init__(self) -> None:
        # Monotonically increasing ids
        self.__match_id: Iterator[int] = count()
        self.__matches: dict[int, Match] = dict()

    def _try[T: Event](self, event: T, room: Room, call: EventCall[T]) -> Room_:
        try:
            call(event, room)
        except PlayerError as error:
            room.reply("error", error)
        return room

    def _call[T: Event](self, event: T, call: Callable[[Match], EventCall[T]]) -> Room_:
        if event.match_id not in self.__matches:
            return None

        match = self.__matches[event.match_id]
        if event.pid in match.players:
            return self._try(event, Room(event), call(match))

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
            return self._try(event, Room(event), self.__matches[event.match_id].join)

    def leave(self, event: PlayerEvent) -> Room_:
        return self._call(event, lambda match: match.leave)

    def draw(self, event: PlayerEvent) -> Room_:
        return self._call(event, lambda match: match.draw)

    def bid(self, event: CardsEvent) -> Room_:
        return self._call(event, lambda match: match.bid)

    def kitty(self, event: CardsEvent) -> Room_:
        return self._call(event, lambda match: match.kitty)

    def play(self, event: CardsEvent) -> Room_:
        return self._call(event, lambda match: match.play)

    def next(self, event: PlayerEvent) -> Room_:
        return self._call(event, lambda match: match.next)
