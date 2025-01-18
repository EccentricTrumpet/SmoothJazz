from itertools import count
from typing import Iterator

from core import Player


class Players:
    def __init__(self, players: list[Player] | None = None) -> None:
        # Monotonically increasing ids
        self.__player_ids: Iterator[int] = count()
        self.__players = {} if players is None else {p.pid: p for p in players}

    def __len__(self) -> int:
        return len(self.__players)

    def __contains__(self, pid: int) -> bool:
        return pid in self.__players

    def __getitem__(self, pid: int) -> Player:
        return self.__players[pid]

    def json(self) -> list[dict]:
        return [player.json() for player in self.__players.values()]

    def add(self, name: str, sid: str) -> Player:
        player = Player(next(self.__player_ids), name, sid)
        self.__players[player.pid] = player
        return player

    def remove(self, pid: int) -> Player:
        return self.__players.pop(pid)

    def first(self) -> Player:
        return next(iter(self.__players.values()))

    def next(self, pid: int, increment=1) -> int:
        if pid not in self.__players:
            raise KeyError(f"No player found for pid: {pid}.")
        pids = list(self.__players.keys())
        return pids[(pids.index(pid) + increment) % len(self.__players)]

    def assign_fixed_team(self, pid: int):
        for i in range(len(self.__players)):
            self[pid].defender = i % 2 == 0
            pid = self.next(pid)

    def attackers(self) -> list[int]:
        return [player.pid for player in self.__players.values() if not player.defender]

    def defenders(self) -> list[int]:
        return [player.pid for player in self.__players.values() if player.defender]
