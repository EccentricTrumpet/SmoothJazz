import random
from typing import List, Sequence
from abstractions.enums import GamePhase, Trump, Suit
from abstractions.types import Card, Player


class Game:
    def __init__(
        self,
        match_id: int,
        players: Sequence[Player],
        lead_player_id: int,
        trump_rank: int,
    ) -> None:
        self.__match_id = match_id
        self.__players = players
        self.__lead_player_id = lead_player_id
        self.__trump_rank = trump_rank

        self.current_player_id = lead_player_id
        self.__phase = GamePhase.DRAW
        self.__trump_state = Trump.NONE
        self.__trump_suit = Suit.UNKNOWN
        self.__score = 0
        self.__kitty: List[Card] = []
        self.__discard: List[Card] = []
        self.deck: List[Card] = []

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

        print("Shuffled deck:")
        for card in self.deck:
            print(card)
