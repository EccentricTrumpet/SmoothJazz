from typing import Sequence
from abstractions import Card
from core.format import Format
from core.order import Order
from core.player import Player


# Logic for managing tricks comprising of a play from each player
class Trick:
    def __init__(self, num_players: int, order: Order) -> None:
        # Inputs
        self.__num_players = num_players
        self.__order = order

        # Private
        self.__lead_id = -1

        # Protected for testing
        self._plays: dict[int, Format] = {}

        # Public
        self.score = 0
        self.winner_id = -1

    @property
    def ended(self) -> bool:
        return len(self._plays) == self.__num_players

    @property
    def winning_play(self) -> Format:
        return self._plays[self.winner_id]

    def __match_format(
        self, lead: Format, play: Format, player_cards: Sequence[Card]
    ) -> bool:
        # TODO: Implement format enforcement and matching
        return True

    def __resolve_format(
        self, other_players: Sequence[Player], player: Player, cards: Sequence[Card]
    ) -> Format | None:
        # Must contain at least one card
        if len(cards) == 0:
            print("Unable to resolve: empty play")
            return None

        # Player must possess the cards
        if not player.has_cards(cards):
            print("Unable to resolve: player does not possess played cards")
            return None

        # Enforce leading play rules
        if self.__lead_id == -1:
            format = Format(self.__order, cards)

            # Format must be suited
            if not format.suited:
                print("Unable to resolve: leading play not suited")
                return None

            # TODO: Enforce toss rules

            return format

        lead = self._plays[self.__lead_id]

        # Enforce follow length
        if len(cards) != lead.length:
            print("Unable to resolve: following play with incorrect length")
            return None

        # Enforce follow suit
        player_cards = player.cards_in_suit(self.__order, lead.suit, lead.all_trumps)
        required_suit_cards = min(len(player_cards), lead.length)
        format = Format(self.__order, cards)

        if len(format.cards_in_suit(lead.suit, lead.all_trumps)) < required_suit_cards:
            print("Unable to resolve: following play without required suit cards")
            return None

        # Partial or mismatched non-trump follow, format need not to be matched
        if not format.all_trumps and format.suit != lead.suit:
            print("Unable to resolve: following play unsuited and contains non-trumps")
            return format

        # Enforce follow trick format
        if not self.__match_format(lead, format, player_cards):
            print("Unable to resolve: following play format mismatch")
            lead.reset()
            return None

        # Resolution successful
        format.reform_with(lead)
        lead.reset()
        return format

    # Checks legality and update trick states
    def try_play(
        self, other_players: Sequence[Player], player: Player, cards: Sequence[Card]
    ) -> bool:
        play_format = self.__resolve_format(other_players, player, cards)
        if play_format is None:
            return False

        # Update states
        self.score += sum([c.points for c in cards])
        self._plays[player.id] = play_format

        # Update lead player id, if needed
        if self.__lead_id == -1:
            self.__lead_id = player.id
            self.winner_id = player.id
            print("Leading play")
            return True

        # Resolve winning hand
        if not play_format.suited:
            print("Losing play: mixed suits")
            return True

        winning = self._plays[self.winner_id]
        if winning.all_trumps and not play_format.all_trumps:
            print("Losing play: did not follow trumps")
            return True

        if (
            not winning.all_trumps
            and not play_format.all_trumps
            and winning.suit != play_format.suit
        ):
            print("Losing play: did not follow non trump suit")
            return True

        play_format.sort()  # This sort is likely redundant
        if play_format.beats(winning):
            print("Winning play")
            self.winner_id = player.id

        return True
