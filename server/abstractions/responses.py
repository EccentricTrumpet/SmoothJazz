from abc import ABC, abstractmethod
from typing import Sequence
from abstractions import Card, GamePhase
from core.player import Player


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
    def __init__(self, event: str, recipient: str, broadcast: bool, include_self: bool):
        self.event = event
        self.recipient = recipient
        self.broadcast = broadcast
        self.include_self = include_self

    @abstractmethod
    def json(self) -> dict:
        pass

    @property
    def event(self):
        return self._event

    @event.setter
    def event(self, event: str):
        self._event = event

    @property
    def recipient(self):
        return self._recipient

    @recipient.setter
    def recipient(self, recipient: str):
        self._recipient = recipient

    @property
    def broadcast(self):
        return self._broadcast

    @broadcast.setter
    def broadcast(self, broadcast: bool):
        self._broadcast = broadcast

    @property
    def include_self(self):
        return self._include_self

    @include_self.setter
    def include_self(self, include_self: bool):
        self._include_self = include_self


class JoinResponse(SocketResponse):
    def __init__(self, recipient: str, id: int, name: str):
        super().__init__("join", recipient, broadcast=True, include_self=True)
        self.__id = id
        self.__name = name

    def json(self) -> dict:
        return {"id": self.__id, "name": self.__name}


class StartResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        active_player_id: int,
        deck_size: int,
        game_rank: int,
        phase: GamePhase,
    ):
        super().__init__("start", recipient, broadcast=True, include_self=True)
        self.__active_player_id = active_player_id
        self.__deck_size = deck_size
        self.__game_rank = game_rank
        self.__phase = phase

    def json(self) -> dict:
        return {
            "activePlayerId": self.__active_player_id,
            "deckSize": self.__deck_size,
            "gameRank": self.__game_rank,
            "phase": self.__phase,
        }


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
        super().__init__("draw", recipient, broadcast, include_self)
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


class BidResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        player_id: int,
        trumps: Sequence[Card],
    ):
        super().__init__("bid", recipient, broadcast=True, include_self=True)
        self.player_id = player_id
        self.trumps = trumps

    def json(self) -> dict:
        return {
            "playerId": self.player_id,
            "trumps": [
                {"id": trump.id, "suit": trump.suit, "rank": trump.rank}
                for trump in self.trumps
            ],
        }


class KittyResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        player_id: int,
        phase: GamePhase,
        cards: Sequence[Card],
        broadcast: bool = False,
        include_self: bool = False,
    ):
        super().__init__("kitty", recipient, broadcast, include_self)
        self.player_id = player_id
        self.phase = phase
        self.cards = cards

    def json(self) -> dict:
        return {
            "playerId": self.player_id,
            "phase": self.phase,
            "cards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self.cards
            ],
        }


class PlayResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        player_id: int,
        active_player_id: int,
        cards: Sequence[Card],
    ):
        super().__init__("play", recipient, broadcast=True, include_self=True)
        self.player_id = player_id
        self.active_player_id = active_player_id
        self.cards = cards

    def json(self) -> dict:
        return {
            "playerId": self.player_id,
            "activePlayerId": self.active_player_id,
            "cards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self.cards
            ],
        }


class TrickResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        score: int,
        active_player_id: int,
        play: PlayResponse,
    ):
        super().__init__("trick", recipient, broadcast=True, include_self=True)
        self.score = score
        self.active_player_id = active_player_id
        self.play = play

    def json(self) -> dict:
        return {
            "score": self.score,
            "activePlayerId": self.active_player_id,
            "play": self.play.json(),
        }


class EndResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        trick: TrickResponse,
        phase: GamePhase,
        kitty_id: int,
        kitty: Sequence[Card],
        lead_id: int,
        score: int,
    ):
        super().__init__("end", recipient, broadcast=True, include_self=True)
        self.trick = trick
        self.phase = phase
        self.kitty_id = kitty_id
        self.kitty = kitty
        self.lead_id = lead_id
        self.score = score

    def json(self) -> dict:
        return {
            "trick": self.trick.json(),
            "phase": self.phase,
            "kittyId": self.kitty_id,
            "kitty": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self.kitty
            ],
            "leadId": self.lead_id,
            "score": self.score,
        }
