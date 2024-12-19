from typing import Sequence
from abstractions.responses import AlertResponse
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
    ) -> AlertResponse | None:
        # TODO: Implement format enforcement and matching
        return None

    def __resolve_format(
        self, other_players: Sequence[Player], player: Player, cards: Sequence[Card]
    ) -> Format | None:
        socket_id = player.socket_id

        # Must contain at least one card
        if len(cards) == 0:
            return AlertResponse(
                socket_id, "Invalid play", "Must play at least 1 card."
            )

        # Player must possess the cards
        if not player.has_cards(cards):
            return AlertResponse(
                socket_id, "Invalid play", "You don't have those cards."
            )

        # Enforce leading play rules
        if self.__lead_id == -1:
            format = Format(self.__order, cards)

            # Format must be suited
            if not format.suited:
                return AlertResponse(
                    socket_id, "Invalid play", "Leading play must be suited."
                )

            # TODO: Enforce toss rules

            return format

        lead = self._plays[self.__lead_id]

        # Enforce follow length
        if len(cards) != lead.length:
            return AlertResponse(socket_id, "Invalid play", "Wrong number of cards.")

        # Enforce follow suit
        player_cards = player.cards_in_suit(self.__order, lead.suit, lead.all_trumps)
        required_suit_cards = min(len(player_cards), lead.length)
        format = Format(self.__order, cards)

        if len(format.cards_in_suit(lead.suit, lead.all_trumps)) < required_suit_cards:
            return AlertResponse(
                socket_id, "Invalid play", "Must follow suit.", player_cards
            )

        # Partial or mismatched non-trump follow, format need not to be matched
        if not format.all_trumps and format.suit != lead.suit:
            return format

        # Enforce follow trick format
        alert = self.__match_format(lead, format, player_cards)
        if alert is not None:
            lead.reset()
            return alert

        # Resolution successful
        format.reform_with(lead)
        lead.reset()
        return format

    # Checks legality and update trick states
    def try_play(
        self, other_players: Sequence[Player], player: Player, cards: Sequence[Card]
    ) -> AlertResponse | None:
        format = self.__resolve_format(other_players, player, cards)
        if isinstance(format, AlertResponse):
            return format

        # Update states
        self.score += sum([c.points for c in cards])
        self._plays[player.id] = format

        # Update lead player id, if needed
        if self.__lead_id == -1:
            self.__lead_id = player.id
            self.winner_id = player.id
            print("Leading play")
            return

        # Resolve winning hand
        if not format.suited:
            print("Losing play: mixed suits")
            return

        winning = self._plays[self.winner_id]
        if winning.all_trumps and not format.all_trumps:
            print("Losing play: did not follow trumps")
            return

        if (
            not winning.all_trumps
            and not format.all_trumps
            and winning.suit != format.suit
        ):
            print("Losing play: did not follow non trump suit")
            return

        format.sort()  # This sort is likely redundant
        if format.beats(winning):
            print("Winning play")
            self.winner_id = player.id
