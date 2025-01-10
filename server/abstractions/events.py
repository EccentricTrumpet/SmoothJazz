from typing import Sequence
from abstractions import Card, Suit


class JoinEvent:
    def __init__(self, sid: str, payload: dict):
        self.sid = sid
        self.match_id = int(payload["matchId"])
        self.player_name: str = payload["playerName"]


class PlayerEvent:
    def __init__(self, sid: str, payload: dict):
        self.sid = sid
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])


class CardsEvent:
    def __init__(self, sid: str, payload: dict):
        self.sid = sid
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])
        self.cards: Sequence[Card] = []
        for card in payload["cards"]:
            self.cards.append(
                Card(int(card["id"]), Suit(card["suit"]), int(card["rank"]))
            )
