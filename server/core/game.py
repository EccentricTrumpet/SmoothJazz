import random
from typing import List, Sequence
from abstractions.enums import GamePhase, Suit, TrumpType
from abstractions.types import Card, Player
from abstractions.requests import DrawRequest, KittyRequest, TrumpRequest
from abstractions.responses import (
    DrawResponse,
    StartResponse,
    KittyResponse,
    TrumpResponse,
)


class Game:
    def __init__(
        self,
        game_id,
        match_id: int,
        num_cards: int,
        game_rank: int,
        lead_player_id: int,
        players: Sequence[Player],
    ) -> None:
        # Inputs
        self.__game_id = game_id
        self.__match_id = match_id
        self.__players = players
        self.__lead_player_id = lead_player_id
        self.__game_rank = game_rank

        # Private
        self.__phase = GamePhase.DRAW
        self.__score = 0
        self.__kitty: List[Card] = []
        self.__discard: List[Card] = []
        self.__deck: List[Card] = []
        self.__trump_declarer_id_id = -1
        self.__trump_suit = Suit.UNKNOWN
        self.__trump_type = TrumpType.NONE
        self.__kitty_player_id = lead_player_id
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

    def start(self) -> StartResponse:
        return StartResponse(
            self.__match_id,
            self.__active_player_id,
            len(self.__deck),
            self.__game_rank,
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
            if len(self.__deck) == 8:
                self.__phase = GamePhase.RESERVE
                self.__active_player_id = self.__kitty_player_id
            else:
                self.__active_player_id = (self.__active_player_id + 1) % len(
                    self.__players
                )

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
            self.__phase = GamePhase.KITTY

            return DrawResponse(
                player.socket_id,
                self.__kitty_player_id,
                self.__phase,
                self.__kitty_player_id,
                cards,
                include_self=True,
            )

    def __resolve_trump_type(self, cards: Sequence[Card]) -> TrumpType:
        if len(cards) == 0:
            return TrumpType.NONE
        if len(cards) == 1 and cards[0].rank == self.__game_rank:
            return TrumpType.SINGLE
        if len(cards) == 2:
            # Must be pairs
            if cards[0].suit == cards[1].suit and cards[0].rank == cards[1].rank:
                if cards[0].suit == Suit.JOKER:
                    return (
                        TrumpType.BIG_JOKER
                        if cards[0].rank == 2
                        else TrumpType.SMALL_JOKER
                    )
                if cards[0].rank == self.__game_rank:
                    return TrumpType.PAIR
        return TrumpType.NONE

    def trump(self, request: TrumpRequest) -> TrumpResponse | None:
        # Can only declare trumps during draw or reserve (抓底牌) phases
        if self.__phase != GamePhase.DRAW and self.__phase != GamePhase.RESERVE:
            return None

        # Player must possess the cards
        if not self.__players[request.player_id].has_cards(request.trumps):
            return None

        trump_type = self.__resolve_trump_type(request.trumps)

        # Allow fortification from a single to a pair by the trump declarer only
        fortify = (
            self.__trump_type == TrumpType.SINGLE
            and trump_type == TrumpType.SINGLE
            and self.__trump_suit == request.trumps[0].suit
            and self.__trump_declarer_id_id == request.player_id
        )

        # Must fortify or declare trump that is of higher priority
        if not fortify and trump_type <= self.__trump_type:
            return None

        # Update states
        self.__trump_suit = request.trumps[0].suit
        self.__trump_type = trump_type
        self.__trump_declarer_id = request.player_id

        # In the first game, the declarer is the kitty player
        if self.__game_id == 0:
            self.__kitty_player_id = self.__trump_declarer_id

        return TrumpResponse(self.__match_id, request.player_id, request.trumps)

    def kitty(self, request: KittyRequest) -> KittyResponse | None:
        # Only hide kitty during the kitty phase
        if self.__phase != GamePhase.KITTY:
            return None

        # Only kitty player can hide kitty
        if request.player_id != self.__kitty_player_id:
            return None

        # Number of cards must be correct
        if len(request.cards) != 8:
            return None

        kitty_player = self.__players[request.player_id]

        # Player must possess the cards
        if not kitty_player.has_cards(request.cards):
            return None

        # Hide kitty
        kitty_player.play(request.cards)
        self.__kitty = request.cards

        # Update states
        self.__phase = GamePhase.PLAY

        return KittyResponse(
            self.__match_id, request.player_id, self.__phase, request.cards, True, True
        )
