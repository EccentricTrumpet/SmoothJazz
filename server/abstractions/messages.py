from abc import ABC, abstractmethod
from typing import Sequence
from abstractions.types import Card, Player
from abstractions.enums import GamePhase


# HTTP responses
class HttpResponse(ABC):
    @abstractmethod
    def json(self) -> dict:
        pass


class MatchResponse(HttpResponse):
    def __init__(
        self, id: int, debug: bool, num_players: int, players: Sequence[Player]
    ):
        self.__id = id
        self.__debug = debug
        self.__num_players = num_players
        self.__players = players

    def json(self) -> dict:
        return {
            "id": self.__id,
            "debug": self.__debug,
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

    def get_recipient(self):
        return self._recipient

    def set_recipient(self, recipient: str):
        self._recipient = recipient

    def get_broadcast(self):
        return self._broadcast

    def set_broadcast(self, broadcast: bool):
        self._broadcast = broadcast

    def get_include_self(self):
        return self._include_self

    def set_include_self(self, include_self: bool):
        self._include_self = include_self

    event = property(get_event, set_event)
    recipient = property(get_recipient, set_recipient)
    broadcast = property(get_broadcast, set_broadcast)
    include_self = property(get_include_self, set_include_self)


class JoinRequest:
    def __init__(self, payload: str, socket_id: str):
        self.match_id = int(payload["matchId"])
        self.player_name: str = payload["playerName"]
        self.socket_id = socket_id


class JoinResponse(SocketResponse):
    def __init__(self, recipient: str, id: int, name: str):
        self.event = "join"
        self.recipient = recipient
        self.broadcast = True
        self.include_self = True
        self.__id = id
        self.__name = name

    def json(self) -> dict:
        return {"id": self.__id, "name": self.__name}


class GameStartResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        active_player_id: int,
        deck_size: int,
        trump_rank: int,
        game_phase: GamePhase,
    ):
        self.event = "gameStart"
        self.recipient = recipient
        self.broadcast = True
        self.include_self = True
        self.__active_player_id = active_player_id
        self.__deck_size = deck_size
        self.__trump_rank = trump_rank
        self.__game_phase = game_phase

    def json(self) -> dict:
        return {
            "activePlayerId": self.__active_player_id,
            "deckSize": self.__deck_size,
            "trumpRank": self.__trump_rank,
            "gamePhase": self.__game_phase,
        }


class DrawRequest:
    def __init__(self, payload: str):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])


class DrawResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        id: int,
        phase: GamePhase,
        activePlayerId: int,
        cards: Sequence[Card],
        broadcast: bool = False,
        include_self: bool = False,
    ):
        self.event = "draw"
        self.recipient = recipient
        self.broadcast = broadcast
        self.include_self = include_self
        self.id = id
        self.phase = phase
        self.activePlayerId = activePlayerId
        self.cards = cards

    def json(self) -> dict:
        return {
            "id": self.id,
            "phase": self.phase,
            "activePlayerId": self.activePlayerId,
            "cards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self.cards
            ],
        }
