from abc import ABC, abstractmethod
from typing import Sequence, Tuple
from abstractions import Card, GamePhase, MatchPhase


# HTTP responses
class HttpResponse(ABC):
    @abstractmethod
    def json(self) -> dict:
        pass


class MatchResponse(HttpResponse):
    def __init__(
        self,
        id: int,
        debug: bool,
        num_players: int,
        phase: MatchPhase,
        players: Sequence[Tuple[int, str, int]],
    ):
        self.__id = id
        self.__debug = debug
        self.__num_players = num_players
        self.__phase = phase
        self.__players = players

    def json(self) -> dict:
        return {
            "id": self.__id,
            "debug": self.__debug,
            "numPlayers": self.__num_players,
            "phase": self.__phase,
            "players": [
                {"id": player[0], "name": player[1], "level": [2]}
                for player in self.__players
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


class AlertResponse(SocketResponse):
    def __init__(
        self, recipient: str, title: str, message: str, hint_cards: Sequence[Card] = []
    ):
        super().__init__("alert", recipient, broadcast=True, include_self=True)
        self._title = title
        self._message = message
        self._hint_cards = hint_cards

    def json(self) -> dict:
        return {
            "title": self._title,
            "message": self._message,
            "hintCards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self._hint_cards
            ],
        }


class JoinResponse(SocketResponse):
    def __init__(self, recipient: str, id: int, name: str, level: int):
        super().__init__("join", recipient, broadcast=True, include_self=True)
        self.__id = id
        self.__name = name
        self.__level = level

    def json(self) -> dict:
        return {"id": self.__id, "name": self.__name, "level": self.__level}


class LeaveResponse(SocketResponse):
    def __init__(self, recipient: str, id: int):
        super().__init__("leave", recipient, broadcast=True, include_self=True)
        self.__id = id

    def json(self) -> dict:
        return {"id": self.__id}


class StartResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        active_player_id: int,
        kitty_player_id: int,
        attackers: Sequence[int],
        defenders: Sequence[int],
        deck_size: int,
        game_rank: int,
        phase: GamePhase,
    ):
        super().__init__("start", recipient, broadcast=True, include_self=True)
        self.__active_player_id = active_player_id
        self.__kitty_player_id = kitty_player_id
        self.__attackers = attackers
        self.__defenders = defenders
        self.__deck_size = deck_size
        self.__game_rank = game_rank
        self.__phase = phase

    def json(self) -> dict:
        return {
            "activePlayerId": self.__active_player_id,
            "kittyPlayerId": self.__kitty_player_id,
            "attackers": [attacker for attacker in self.__attackers],
            "defenders": [defender for defender in self.__defenders],
            "deckSize": self.__deck_size,
            "gameRank": self.__game_rank,
            "phase": self.__phase,
        }


class MatchPhaseResponse(SocketResponse):
    def __init__(
        self,
        recipient: str,
        phase: MatchPhase,
    ):
        super().__init__("phase", recipient, broadcast=True, include_self=True)
        self.__phase = phase

    def json(self) -> dict:
        return {
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
        kitty_player_id: int,
        attackers: Sequence[int],
        defenders: Sequence[int],
    ):
        super().__init__("bid", recipient, broadcast=True, include_self=True)
        self.player_id = player_id
        self.trumps = trumps
        self.__kitty_player_id = kitty_player_id
        self.__attackers = attackers
        self.__defenders = defenders

    def json(self) -> dict:
        return {
            "playerId": self.player_id,
            "trumps": [
                {"id": trump.id, "suit": trump.suit, "rank": trump.rank}
                for trump in self.trumps
            ],
            "kittyPlayerId": self.__kitty_player_id,
            "attackers": [attacker for attacker in self.__attackers],
            "defenders": [defender for defender in self.__defenders],
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
        trick_winner_id: int,
        cards: Sequence[Card],
    ):
        super().__init__("play", recipient, broadcast=True, include_self=True)
        self.player_id = player_id
        self.active_player_id = active_player_id
        self.trick_winner_id = trick_winner_id
        self.cards = cards

    def json(self) -> dict:
        return {
            "playerId": self.player_id,
            "activePlayerId": self.active_player_id,
            "trickWinnerId": self.trick_winner_id,
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
        players: Sequence[Tuple[int, int]],
    ):
        super().__init__("end", recipient, broadcast=True, include_self=True)
        self.trick = trick
        self.phase = phase
        self.kitty_id = kitty_id
        self.kitty = kitty
        self.lead_id = lead_id
        self.score = score
        self.players = players

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
            "players": [
                {"id": player[0], "level": player[1]} for player in self.players
            ],
        }
