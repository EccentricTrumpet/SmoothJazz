from abstractions import Cards, PlayerError, Suit
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

    def __infer_format(self, player: Player, cards: Cards) -> Format | None:
        # Must contain at least one card
        if len(cards) == 0:
            raise PlayerError("Invalid play", "Must play at least 1 card.")

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
            lead.validate_follow(cards, played_suit)
        except PlayerError:
            lead.reset()
            raise

        # Inference successful
        format.reform(lead)
        lead.reset()
        return format

    # Checks legality and update trick states
    def play(self, player: Player, cards: Cards) -> None:
        # Resolve format
        format = self.__infer_format(player, cards)

        # Remove cards from player's hand
        player.play(cards)

        # Update states
        self.score += sum([c.points for c in cards])
        self._plays[player.pid] = format

        # Update lead player id, if needed
        if self.__lead_pid == -1:
            self.__lead_pid = player.pid
            self.winner_pid = player.pid
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
                self.winner_pid = player.pid
