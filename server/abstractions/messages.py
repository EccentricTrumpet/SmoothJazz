from abc import ABC, abstractmethod
import json
from typing import Sequence
from abstractions.types import Card, Player


# HTTP responses
class HttpResponse(ABC):
    @abstractmethod
    def json(self) -> dict:
        pass


class MatchResponse(HttpResponse):
    def __init__(self, id: int, num_players: int, players: Sequence[Player]):
        self.__id = id
        self.__num_players = num_players
        self.__players = players

    def json(self) -> dict:
        return {
            "id": self.__id,
            "numPlayers": self.__num_players,
            "players": [
                {"id": player.id, "name": player.name} for player in self.__players
            ],
        }


# Socket responses
class SocketResponse(ABC):
    @abstractmethod
    def json(self) -> dict:
        pass

    def get_event(self):
        return self._event

    def set_event(self, event: str):
        self._event = event

    event = property(get_event, set_event)

    def get_recipient(self):
        return self._recipient

    def set_recipient(self, recipient: str):
        self._recipient = recipient

    recipient = property(get_recipient, set_recipient)


class JoinRequest:
    def __init__(self, payload: str, socket_id: str):
        self.match_id = int(payload["matchId"])
        self.player_name: str = payload["playerName"]
        self.socket_id = socket_id


class JoinResponse(SocketResponse):
    def __init__(self, recipient: str, id: int, name: str):
        self.event = "join"
        self.recipient = recipient
        self.__id = id
        self.__name = name

    def json(self) -> dict:
        return {"id": self.__id, "name": self.__name}


class GameStartResponse(SocketResponse):
    def __init__(self, recipient: str, current_player_id: int, deck: Sequence[Card]):
        self.event = "gameStart"
        self.recipient = recipient
        self.__current_player_id = current_player_id
        self.__deck = deck

    def json(self) -> dict:
        return {
            "current_player_id": self.__current_player_id,
            "deck": [card.id for card in self.__deck],
        }
