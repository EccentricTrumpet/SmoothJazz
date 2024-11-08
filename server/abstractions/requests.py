from typing import Sequence
from abstractions.types import Card
from abstractions.enums import Suit


class JoinRequest:
    def __init__(self, payload: dict, socket_id: str):
        self.match_id = int(payload["matchId"])
        self.player_name: str = payload["playerName"]
        self.socket_id: str = socket_id


class DrawRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])


class TrumpRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])
        self.trumps: Sequence[Card] = []
        for trump in payload["trumps"]:
            self.trumps.append(
                Card(int(trump["id"]), Suit(trump["suit"]), int(trump["rank"]))
            )
