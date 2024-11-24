from typing import Sequence
from core.format import Format
from core.order import Order
from abstractions.types import Card
from core.player import Player


# Logic for managing tricks comprising of a play from each player
class Trick:
    def __init__(self, num_players: int, order: Order) -> None:
        self.__num_players = num_players
        self.__order = order
        self.__plays: dict[int, Format] = {}
        self.score = 0
        self.lead_id = -1
        self.winner_id = -1

    def __match_format(
        self, lead: Format, play: Format, player_cards: Sequence[Card]
    ) -> bool:
        return True

    def __resolve_format(
        self, other_players: Sequence[Player], player: Player, cards: Sequence[Card]
    ) -> Format | None:
        # Must contain at least one card
        if len(cards) == 0:
            print("Unable to resolve format: empty play")
            return None

        # Player must possess the cards
        if not player.has_cards(cards):
            print("Unable to resolve format: player does not possess played cards")
            return None

        # Enforce leading play rules
        if self.lead_id == -1:
            format = Format(self.__order, cards)

            # Format must be suited
            if not format.suited:
                print("Unable to resolve format: leading play not suited")
                return None

            # Enforce toss rules

            return format

        lead = self.__plays[self.lead_id]

        # Enforce follow length
        if len(cards) != lead.length:
            print("Unable to resolve format: following play with incorrect length")
            return None

        # Enforce follow suit
        player_cards = player.cards_in_suit(self.__order, lead.suit, lead.all_trumps)
        required_suit_cards = min(len(player_cards), lead.length)
        format = Format(self.__order, cards)

        if len(format.cards_in_suit(lead.suit, lead.all_trumps)) < required_suit_cards:
            print(
                "Unable to resolve format: following play without required suit cards"
            )
            return None

        # Partial or mismatched non-trump follow, format need not to be matched
        if not format.all_trumps and format.suit != lead.suit:
            return format

        # Enforce follow trick format
        if self.__match_format(lead, format, player_cards):
            # format.reform_with(lead)
            lead.reset()
            return format

        lead.reset()
        return None

    # Checks legality and update trick states
    def try_play(
        self, other_players: Sequence[Player], player: Player, cards: Sequence[Card]
    ) -> bool:
        play_format = self.__resolve_format(other_players, player, cards)
        if play_format == None:
            return False

        # Record played cards
        self.__plays[player.id] = play_format

        # Update lead player id, if needed
        if self.lead_id == -1:
            self.lead_id = player.id
            # Mock logic
            self.winner_id = (self.lead_id + 1) % self.__num_players

        # Update states
        self.score += sum([c.points() for c in cards])

        return True

    def is_done(self) -> bool:
        return len(self.__plays) == self.__num_players
