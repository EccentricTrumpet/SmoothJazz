from abstractions import Cards, GamePhase, MatchPhase, PInfos, PlayerInfo, Suit, Update


class PlayerUpdate(Update):
    def __init__(self, player_info: PlayerInfo) -> None:
        self.player_info = player_info

    def json(self, _: bool = False) -> dict:
        return self.player_info.json()


class StartUpdate(Update):
    def __init__(self, active_pid: int, cards: int, rank: int) -> None:
        self.active_pid = active_pid
        self.cards = cards
        self.rank = rank

    def json(self, _: bool = False) -> dict:
        return {"activePid": self.active_pid, "cards": self.cards, "rank": self.rank}


class TeamUpdate(Update):
    def __init__(self, kitty_pid: int, defenders: list[int]) -> None:
        self.kitty_pid = kitty_pid
        self.defenders = defenders

    def json(self, _: bool = False) -> dict:
        return {"kittyPid": self.kitty_pid, "defenders": self.defenders}


class MatchUpdate(Update):
    def __init__(self, phase: MatchPhase) -> None:
        self.phase = phase

    def json(self, _: bool = False) -> dict:
        return {"phase": self.phase}


class DrawUpdate(Update):
    def __init__(
        self, id: int, phase: GamePhase, active_pid: int, cards: Cards
    ) -> None:
        self.id = id
        self.phase = phase
        self.active_pid = active_pid
        self.cards = cards

    def json(self, secret: bool = False) -> dict:
        return {
            "id": self.id,
            "phase": self.phase,
            "activePlayerId": self.active_pid,
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
    def __init__(self, pid: int, trumps: Cards, kitty_pid: int) -> None:
        self.pid = pid
        self.trumps = trumps
        self.__kitty_pid = kitty_pid

    def json(self, _: bool = False) -> dict:
        return {
            "playerId": self.pid,
            "trumps": [
                {"id": trump.id, "suit": trump.suit, "rank": trump.rank}
                for trump in self.trumps
            ],
            "kittyPlayerId": self.__kitty_pid,
        }


class KittyUpdate(Update):
    def __init__(self, pid: int, phase: GamePhase, cards: Cards) -> None:
        self.pid = pid
        self.phase = phase
        self.cards = cards

    def json(self, secret: bool = False) -> dict:
        return {
            "playerId": self.pid,
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
        pid: int,
        active_pid: int,
        cards: Cards,
        winner_pid: int | None = None,
        score: int | None = None,
    ) -> None:
        self.pid = pid
        self.active_pid = active_pid
        self.winner_pid = winner_pid
        self.cards = cards
        self.score = score

    def json(self, _: bool = False) -> dict:
        json = {
            "pid": self.pid,
            "activePid": self.active_pid,
            "cards": [card.json() for card in self.cards],
        }
        if self.winner_pid is not None:
            json["winnerPid"] = self.winner_pid
        if self.score is not None:
            json["score"] = self.score
        return json


class EndUpdate(Update):
    def __init__(self, play: PlayUpdate, kitty: PlayUpdate, players: PInfos) -> None:
        self.play = play
        self.kitty = kitty
        self.players = players

    def json(self, secret: bool = False) -> dict:
        return {
            "play": self.play.json(secret),
            "kitty": self.kitty.json(secret),
            "players": [player.json() for player in self.players],
        }
