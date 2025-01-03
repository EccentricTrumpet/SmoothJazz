from typing import Sequence
from abstractions.responses import AlertResponse
from abstractions import Card, Suit
from core import Order, Player
from core.format import Format


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
        hand_cards = player.cards_in_suit(self.__order, lead.suit, lead.trumps)
        required_suit_cards = min(len(hand_cards), lead.length)
        format = Format(self.__order, cards)

        if len(format.cards_in_suit(lead.suit, lead.trumps)) < required_suit_cards:
            return AlertResponse(
                socket_id, "Invalid play", "Must follow suit.", hand_cards
            )

        # Partial or mismatched non-trump follow, format need not to be matched
        if not (
            # Need to check if format is all trumps
            format.trumps
            # Need to check if format matches lead suit and suit is not Suit.UNKNOWN
            or (format.suit == lead.suit and format.suit != Suit.UNKNOWN)
        ):
            return format

        # Enforce follow trick format
        played_suit = (
            # If following non-trump with trumps, there's no need to enforce format.
            # To bypass the format check, pretend the cards played are the ones in hand.
            cards
            if not lead.trumps and format.trumps
            else player.cards_in_suit(self.__order, lead.suit, format.trumps)
        )
        alert = lead.resolve_play(cards, played_suit)
        if alert is not None:
            lead.reset()
            alert.recipient = socket_id
            return alert

        # Resolution successful
        format.try_reform(lead)
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
        if winning.trumps and not format.trumps:
            print("Losing play: did not follow trumps")
            return

        if not winning.trumps and not format.trumps and winning.suit != format.suit:
            print("Losing play: did not follow non trump suit")
            return

        if format.beats(winning):
            print("Winning play")
            self.winner_id = player.id
