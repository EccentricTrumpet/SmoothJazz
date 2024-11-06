import random
from typing import List, Sequence
from abstractions.enums import GamePhase, Trump, Suit
from abstractions.types import Card, Player
from abstractions.messages import DrawRequest, DrawResponse


class Game:
    def __init__(
        self,
        match_id: int,
        players: Sequence[Player],
        lead_player_id: int,
        trump_rank: int,
    ) -> None:
        # Inputs
        self.__match_id = match_id
        self.__players = players
        self.__lead_player_id = lead_player_id
        self.__trump_rank = trump_rank

        # Private
        self.__trump_state = Trump.NONE
        self.__trump_suit = Suit.UNKNOWN
        self.__score = 0
        self.__kitty: List[Card] = []
        self.__discard: List[Card] = []

        # Public
        self.phase = GamePhase.DRAW
        self.deck: List[Card] = []
        self.active_player_id = lead_player_id

        # 1 deck for every 2 players, rounded down
        indices = list(range(54 * (len(self.__players) // 2)))
        random.shuffle(indices)  # Pre-shuffle indices it won't match card order
        suits = list(Suit)

        for i in range(54 * (len(self.__players) // 2)):
            card_index = i % 54
            suit_index = card_index // 13
            rank_index = card_index % 13 + 1
            self.deck.append(Card(indices[i], suits[suit_index], rank_index))

        random.shuffle(self.deck)

    def draw(self, request: DrawRequest) -> DrawResponse | None:
        if request.player_id != self.active_player_id:
            return None

        if self.phase == GamePhase.DRAW:
            # Draw card
            card = self.deck.pop()
            player = self.__players[request.player_id]
            player.draw([card])

            # Update states
            self.active_player_id = (self.active_player_id + 1) % len(self.__players)
            if len(self.deck) == 8:
                self.phase = GamePhase.RESERVE

            return DrawResponse(
                player.socket_id,
                player.id,
                self.phase,
                self.active_player_id,
                [card],
                include_self=True,
            )

        elif self.phase == GamePhase.RESERVE:
            # Draw cards
            cards = self.deck
            player = self.__players[request.player_id]
            player.draw(cards)

            # Update states
            self.deck = []
            self.phase == GamePhase.KITTY

            return DrawResponse(
                player.socket_id,
                self.active_player_id,
                self.phase,
                self.active_player_id,
                cards,
                include_self=True,
            )
