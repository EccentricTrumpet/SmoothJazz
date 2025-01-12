from abstractions import Cards, GamePhase, MatchPhase, PlayerInfo, Suit, Update


class PlayerUpdate(Update):
    def __init__(self, player_info: PlayerInfo):
        self.player_info = player_info

    def json(self, _: bool = False) -> dict:
        return self.player_info.json()


class StartUpdate(Update):
    def __init__(
        self,
        active_pid: int,
        kitty_pid: int,
        attackers: list[int],
        defenders: list[int],
        deck_size: int,
        game_rank: int,
        phase: GamePhase,
    ):
        self.__active_pid = active_pid
        self.__kitty_pid = kitty_pid
        self.__attackers = attackers
        self.__defenders = defenders
        self.__deck_size = deck_size
        self.__game_rank = game_rank
        self.__phase = phase

    def json(self, _: bool = False) -> dict:
        return {
            "activePlayerId": self.__active_pid,
            "kittyPlayerId": self.__kitty_pid,
            "attackers": [attacker for attacker in self.__attackers],
            "defenders": [defender for defender in self.__defenders],
            "deckSize": self.__deck_size,
            "gameRank": self.__game_rank,
            "phase": self.__phase,
        }


class MatchUpdate(Update):
    def __init__(self, phase: MatchPhase):
        self.__phase = phase

    def json(self, _: bool = False) -> dict:
        return {"phase": self.__phase}


class DrawUpdate(Update):
    def __init__(self, id: int, phase: GamePhase, activePlayerId: int, cards: Cards):
        self.id = id
        self.phase = phase
        self.activePlayerId = activePlayerId
        self.cards = cards

    def json(self, secret: bool = False) -> dict:
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
        pid: int,
        trumps: Cards,
        kitty_pid: int,
        attackers: list[int],
        defenders: list[int],
    ):
        self.pid = pid
        self.trumps = trumps
        self.__kitty_pid = kitty_pid
        self.__attackers = attackers
        self.__defenders = defenders

    def json(self, _: bool = False) -> dict:
        return {
            "playerId": self.pid,
            "trumps": [
                {"id": trump.id, "suit": trump.suit, "rank": trump.rank}
                for trump in self.trumps
            ],
            "kittyPlayerId": self.__kitty_pid,
            "attackers": [attacker for attacker in self.__attackers],
            "defenders": [defender for defender in self.__defenders],
        }


class KittyUpdate(Update):
    def __init__(self, pid: int, phase: GamePhase, cards: Cards):
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
    ):
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
    def __init__(
        self,
        play: PlayUpdate,
        kitty: PlayUpdate,
        phase: GamePhase,
        players: list[PlayerInfo],
    ):
        self.play = play
        self.phase = phase
        self.kitty = kitty
        self.players = players

    def json(self, secret: bool = False) -> dict:
        return {
            "play": self.play.json(secret),
            "kitty": self.kitty.json(secret),
            "phase": self.phase,
            "players": [player.json() for player in self.players],
        }
