from typing import Sequence
from abstractions import Card, Suit


class JoinRequest:
    def __init__(self, payload: dict, socket_id: str):
        self.match_id = int(payload["matchId"])
        self.player_name: str = payload["playerName"]
        self.socket_id: str = socket_id


class LeaveRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])


class DrawRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])
        print(f"Received draw request for player: {self.player_id}")


class BidRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])
        self.cards: Sequence[Card] = []
        for card in payload["cards"]:
            self.cards.append(
                Card(int(card["id"]), Suit(card["suit"]), int(card["rank"]))
            )


class KittyRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])
        self.cards: Sequence[Card] = []
        for card in payload["cards"]:
            self.cards.append(
                Card(int(card["id"]), Suit(card["suit"]), int(card["rank"]))
            )


class PlayRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])
        self.cards: Sequence[Card] = []
        for card in payload["cards"]:
            self.cards.append(
                Card(int(card["id"]), Suit(card["suit"]), int(card["rank"]))
            )


class NextRequest:
    def __init__(self, payload: dict):
        self.match_id = int(payload["matchId"])
        self.player_id = int(payload["playerId"])
