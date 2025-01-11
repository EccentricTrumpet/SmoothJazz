from typing import Sequence

from abstractions import Card, PlayerError, Room, Suit
from core import Order, Player
from core.format import Format


# Logic for managing tricks comprising of a play from each player
class Trick:
    def __init__(self, num_players: int, order: Order) -> None:
        # Inputs
        self.__num_players = num_players
        self.__order = order

        # Private
        self.__lead_pid = -1

        # Protected for testing
        self._plays: dict[int, Format] = {}

        # Public
        self.score = 0
        self.winner_pid = -1

    @property
    def ended(self) -> bool:
        return len(self._plays) == self.__num_players

    @property
    def winning_play(self) -> Format:
        return self._plays[self.winner_pid]

    def __resolve_format(
        self,
        others: Sequence[Player],
        player: Player,
        cards: Sequence[Card],
        room: Room,
    ) -> Format | None:
        # Must contain at least one card
        if len(cards) == 0:
            raise PlayerError("Invalid play", "Must play at least 1 card.")

        # Player must possess the cards
        if not player.has_cards(cards):
            raise PlayerError("Invalid play", "You don't have those cards.")

        # Enforce leading play rules
        if self.__lead_pid == -1:
            format = Format(self.__order, cards)

            # Format must be suited
            if not format.suited:
                raise PlayerError("Invalid play", "Leading play must be suited.")

            # TODO: Enforce toss rules

            return format

        lead = self._plays[self.__lead_pid]

        # Enforce follow length
        if len(cards) != lead.length:
            raise PlayerError("Invalid play", "Wrong number of cards.")

        # Enforce follow suit
        hand_cards = player.cards_in_suit(self.__order, lead.suit, lead.trumps)
        required_suit_cards = min(len(hand_cards), lead.length)
        format = Format(self.__order, cards)

        if len(format.cards_in_suit(lead.suit, lead.trumps)) < required_suit_cards:
            raise PlayerError("Invalid play", "Must follow suit.", hand_cards)

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

        try:
            lead.play(cards, played_suit, room)
        except PlayerError:
            lead.reset()
            raise

        # Resolution successful
        format.reform(lead)
        lead.reset()
        return format

    # Checks legality and update trick states
    def play(
        self,
        others: Sequence[Player],
        player: Player,
        cards: Sequence[Card],
        room: Room,
    ) -> None:
        format = self.__resolve_format(others, player, cards, room)

        # Update states
        self.score += sum([c.points for c in cards])
        self._plays[player.id] = format

        # Update lead player id, if needed
        if self.__lead_pid == -1:
            self.__lead_pid = player.id
            self.winner_pid = player.id
            print("Leading play")
        else:
            # Resolve winning hand
            winner = self._plays[self.winner_pid]
            if not format.suited:
                print("Losing play: mixed suits")
            elif winner.trumps and not format.trumps:
                print("Losing play: did not follow trumps")
            elif not winner.trumps and not format.trumps and winner.suit != format.suit:
                print("Losing play: did not follow non trump suit")
            elif format.beats(winner):
                print("Winning play")
                self.winner_pid = player.id
