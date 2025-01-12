from abstractions import Cards, GamePhase, HttpResponse, MatchPhase, Suit, Update


class PlayerUpdate(Update):
    def __init__(self, pid: int, name: str = "", level: int = -1):
        self.__pid = pid
        self.__name = name
        self.__level = level

    def json(self, _: bool = False) -> dict:
        return {"id": self.__pid, "name": self.__name, "level": self.__level}


class MatchUpdate(Update):
    def __init__(self, phase: MatchPhase):
        self.__phase = phase

    def json(self, _: bool = False) -> dict:
        return {"phase": self.__phase}


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
    def __init__(self, pid: int, active_pid: int, winner_pid: int, cards: Cards):
        self.pid = pid
        self.active_pid = active_pid
        self.winner_pid = winner_pid
        self.cards = cards

    def json(self, _: bool = False) -> dict:
        return {
            "playerId": self.pid,
            "activePlayerId": self.active_pid,
            "trickWinnerId": self.winner_pid,
            "cards": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self.cards
            ],
        }


class TrickUpdate(Update):
    def __init__(self, play: PlayUpdate, score: int, active_pid: int):
        self.score = score
        self.active_pid = active_pid
        self.play = play

    def json(self, secret: bool = False) -> dict:
        return {
            "score": self.score,
            "activePlayerId": self.active_pid,
            "play": self.play.json(secret),
        }


class EndUpdate(Update):
    def __init__(
        self,
        trick: TrickUpdate,
        phase: GamePhase,
        kitty_pid: int,
        kitty: Cards,
        lead_pid: int,
        score: int,
        players: list[PlayerUpdate],
    ):
        self.trick = trick
        self.phase = phase
        self.kitty_pid = kitty_pid
        self.kitty = kitty
        self.lead_pid = lead_pid
        self.score = score
        self.players = players

    def json(self, secret: bool = False) -> dict:
        return {
            "trick": self.trick.json(secret),
            "phase": self.phase,
            "kittyId": self.kitty_pid,
            "kitty": [
                {"id": card.id, "suit": card.suit, "rank": card.rank}
                for card in self.kitty
            ],
            "leadId": self.lead_pid,
            "score": self.score,
            "players": [player.json() for player in self.players],
        }


class MatchResponse(HttpResponse):
    def __init__(
        self,
        id: int,
        debug: bool,
        num_players: int,
        phase: MatchPhase,
        players: list[PlayerUpdate],
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
            "players": [player.json() for player in self.__players],
        }
