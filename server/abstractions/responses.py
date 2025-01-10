from abc import ABC, abstractmethod
from typing import Sequence, Tuple
from abstractions import Card, GamePhase, HttpResponse, MatchPhase, Suit, Update


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


class PlayerUpdate(Update):
    def __init__(self, id: int, name: str = "", level: int = -1):
        self.__id = id
        self.__name = name
        self.__level = level

    def json(self, _: bool) -> dict:
        return {"id": self.__id, "name": self.__name, "level": self.__level}


class AlertUpdate(Update):
    def __init__(self, title: str, message: str, hint_cards: Sequence[Card] = []):
        self._title = title
        self._message = message
        self._hint_cards = hint_cards

    def json(self, _: bool) -> dict:
        return {
            "title": self._title,
            "message": self._message,
            "hintCards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self._hint_cards
            ],
        }


class MatchUpdate(Update):
    def __init__(self, phase: MatchPhase):
        self.__phase = phase

    def json(self, _: bool) -> dict:
        return {"phase": self.__phase}


class StartUpdate(Update):
    def __init__(
        self,
        active_player_id: int,
        kitty_player_id: int,
        attackers: Sequence[int],
        defenders: Sequence[int],
        deck_size: int,
        game_rank: int,
        phase: GamePhase,
    ):
        self.__active_player_id = active_player_id
        self.__kitty_player_id = kitty_player_id
        self.__attackers = attackers
        self.__defenders = defenders
        self.__deck_size = deck_size
        self.__game_rank = game_rank
        self.__phase = phase

    def json(self, _: bool) -> dict:
        return {
            "activePlayerId": self.__active_player_id,
            "kittyPlayerId": self.__kitty_player_id,
            "attackers": [attacker for attacker in self.__attackers],
            "defenders": [defender for defender in self.__defenders],
            "deckSize": self.__deck_size,
            "gameRank": self.__game_rank,
            "phase": self.__phase,
        }


class DrawUpdate(Update):
    def __init__(
        self, id: int, phase: GamePhase, activePlayerId: int, cards: Sequence[Card]
    ):
        self.id = id
        self.phase = phase
        self.activePlayerId = activePlayerId
        self.cards = cards

    def json(self, secret: bool) -> dict:
        return {
            "id": self.id,
            "phase": self.phase,
            "activePlayerId": self.activePlayerId,
            "cards": [
                {
                    "id": card.id,
                    "suit": Suit.UNKNOWN if secret else card.suit,
                    "rank": 0 if secret else card.rank,
                }
                for card in self.cards
            ],
        }


class BidUpdate(Update):
    def __init__(
        self,
        player_id: int,
        trumps: Sequence[Card],
        kitty_player_id: int,
        attackers: Sequence[int],
        defenders: Sequence[int],
    ):
        self.player_id = player_id
        self.trumps = trumps
        self.__kitty_player_id = kitty_player_id
        self.__attackers = attackers
        self.__defenders = defenders

    def json(self, _: bool) -> dict:
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


class KittyUpdate(Update):
    def __init__(self, player_id: int, phase: GamePhase, cards: Sequence[Card]):
        self.player_id = player_id
        self.phase = phase
        self.cards = cards

    def json(self, secret: bool) -> dict:
        return {
            "playerId": self.player_id,
            "phase": self.phase,
            "cards": [
                {
                    "id": card.id,
                    "suit": Suit.UNKNOWN if secret else card.suit,
                    "rank": 0 if secret else card.rank,
                }
                for card in self.cards
            ],
        }


class PlayUpdate(Update):
    def __init__(
        self,
        player_id: int,
        active_player_id: int,
        trick_winner_id: int,
        cards: Sequence[Card],
    ):
        self.player_id = player_id
        self.active_player_id = active_player_id
        self.trick_winner_id = trick_winner_id
        self.cards = cards

    def json(self, _: bool) -> dict:
        return {
            "playerId": self.player_id,
            "activePlayerId": self.active_player_id,
            "trickWinnerId": self.trick_winner_id,
            "cards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self.cards
            ],
        }


class TrickUpdate(Update):
    def __init__(
        self,
        play: PlayUpdate,
        score: int,
        active_player_id: int,
    ):
        self.score = score
        self.active_player_id = active_player_id
        self.play = play

    def json(self, secret: bool) -> dict:
        return {
            "score": self.score,
            "activePlayerId": self.active_player_id,
            "play": self.play.json(secret),
        }


class EndUpdate(Update):
    def __init__(
        self,
        trick: TrickUpdate,
        phase: GamePhase,
        kitty_id: int,
        kitty: Sequence[Card],
        lead_id: int,
        score: int,
        players: Sequence[Tuple[int, int]],
    ):
        self.trick = trick
        self.phase = phase
        self.kitty_id = kitty_id
        self.kitty = kitty
        self.lead_id = lead_id
        self.score = score
        self.players = players

    def json(self, secret: bool) -> dict:
        return {
            "trick": self.trick.json(secret),
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
