import random
from typing import List, Sequence
from abstractions.enums import GamePhase, Trump, Suit
from abstractions.types import Card, Player
from abstractions.messages import DrawRequest, DrawResponse, GameStartResponse


class Game:
    def __init__(
        self,
        match_id: int,
        num_cards: int,
        trump_rank: int,
        lead_player_id: int,
        players: Sequence[Player],
    ) -> None:
        # Inputs
        self.__match_id = match_id
        self.__players = players
        self.__lead_player_id = lead_player_id
        self.__trump_rank = trump_rank

        # Private
        self.__phase = GamePhase.DRAW
        self.__trump_state = Trump.NONE
        self.__trump_suit = Suit.UNKNOWN
        self.__score = 0
        self.__kitty: List[Card] = []
        self.__discard: List[Card] = []
        self.__deck: List[Card] = []
        self.__active_player_id = lead_player_id

        # 1 deck for every 2 players, rounded down
        indices = list(range(num_cards))
        random.shuffle(indices)  # Pre-shuffle indices it won't match card order
        suits = list(Suit)

        for i in range(num_cards):
            card_index = i % 54
            suit_index = card_index // 13
            rank_index = card_index % 13 + 1
            self.__deck.append(Card(indices[i], suits[suit_index], rank_index))

        random.shuffle(self.__deck)

    def start(self) -> GameStartResponse:
        return GameStartResponse(
            self.__match_id,
            self.__active_player_id,
            len(self.__deck),
            self.__trump_rank,
            self.__phase,
        )

    def draw(self, request: DrawRequest) -> DrawResponse | None:
        if request.player_id != self.__active_player_id:
            return None

        if self.__phase == GamePhase.DRAW:
            # Draw card
            card = self.__deck.pop()
            player = self.__players[request.player_id]
            player.draw([card])

            # Update states
            self.__active_player_id = (self.__active_player_id + 1) % len(
                self.__players
            )
            if len(self.__deck) == 8:
                self.__phase = GamePhase.RESERVE

            return DrawResponse(
                player.socket_id,
                player.id,
                self.__phase,
                self.__active_player_id,
                [card],
                include_self=True,
            )

        elif self.__phase == GamePhase.RESERVE:
            # Draw cards
            cards = self.__deck
            player = self.__players[request.player_id]
            player.draw(cards)

            # Update states
            self.__deck = []
            self.__phase == GamePhase.KITTY

            return DrawResponse(
                player.socket_id,
                self.__active_player_id,
                self.__phase,
                self.__active_player_id,
                cards,
                include_self=True,
            )
