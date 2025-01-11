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
        self.pid = int(payload["playerId"])


class CardsEvent(PlayerEvent):
    def __init__(self, sid: str, payload: dict):
        super().__init__(sid, payload)
        self.cards: Sequence[Card] = []
        for card in payload["cards"]:
            self.cards.append(
                Card(int(card["id"]), Suit(card["suit"]), int(card["rank"]))
            )
