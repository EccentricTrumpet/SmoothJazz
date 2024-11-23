from typing import Sequence
from core.format import Format
from core.order import Order
from abstractions.types import Card, Player


# Logic for managing tricks comprising of a play from each player
class Trick:
    def __init__(self, num_players: int, order: Order) -> None:
        self.__num_players = num_players
        self.__order = order
        self.__plays: dict[int, Format] = {}
        self.score = 0
        self.lead_id = -1
        self.winner_id = -1

    def __is_legal(self, player: Player, cards: Sequence[Card]) -> bool:
        # Must contain at least one card
        if len(cards) == 0:
            return False

        # Player must possess the cards
        if not player.has_cards(cards):
            return False

        # Enforce leading play rules
        if self.lead_id == -1:
            # Enforce toss rules if needed
            return True

        # Enforce follow rules - suit

        # Enforce follow rules - trick format

        return True

    # Checks legality and update trick states
    def try_play(self, player: Player, cards: Sequence[Card]) -> bool:
        if not self.__is_legal(player, cards):
            return False

        # Record played cards
        self.__plays[player.id] = Format(self.__order, cards)

        # Update lead player id, if needed
        if self.lead_id == -1:
            self.lead_id = player.id

        # Update states - mock logic
        if self.winner_id == -1:
            self.winner_id = (self.lead_id + 1) % self.__num_players
            self.score = 5

        return True

    def is_done(self) -> bool:
        return len(self.__plays) == self.__num_players
