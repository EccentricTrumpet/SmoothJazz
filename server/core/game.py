from bisect import bisect_left, bisect_right
import random
from typing import List, Sequence, Set
from abstractions import Card, GamePhase, Suit, TrumpType
from abstractions.requests import DrawRequest, KittyRequest, PlayRequest, BidRequest
from abstractions.responses import (
    DrawResponse,
    EndResponse,
    PlayResponse,
    SocketResponse,
    StartResponse,
    KittyResponse,
    TrickResponse,
    BidResponse,
)
from core.order import Order
from core.trick import Trick
from core.player import Player

END_LEVEL = 15
BOSS_LEVELS = [2, 5, 10, 13, 14, END_LEVEL]  # Level 14 is Aces
CARDS_PER_DECK = 54
CARDS_PER_SUIT = 13
THRESHOLD_PER_DECK = 20


class Game:
    def __init__(
        self,
        game_id,
        match_id: int,
        num_decks: int,
        lead_player_id: int,
        players: Sequence[Player],
    ) -> None:
        # Inputs
        self.__game_id = game_id
        self.__match_id = match_id
        self.__num_decks = num_decks
        self.__players = players

        # Private
        self.__phase = GamePhase.DRAW
        self.__deck: List[Card] = []
        self.__bidder_id = -1
        self.__trump_suit = Suit.UNKNOWN
        self.__trump_type = TrumpType.NONE
        self.__kitty_player_id = lead_player_id
        self.__active_player_id = lead_player_id
        self.__game_rank = self.__players[lead_player_id].level
        self.__order = Order(self.__game_rank)
        self.__ready_players: Set[int] = set()

        # Protected for testing
        self._score = 0
        self._kitty: List[Card] = []
        self._tricks: List[Trick] = []
        self._attackers: Set[int] = set()
        self._defenders: Set[int] = set()

        # Public
        self.next_lead_id = -1

        # Fix game rank for Aces game
        if self.__game_rank > CARDS_PER_SUIT:
            self.__game_rank -= CARDS_PER_SUIT

        # 1 deck for every 2 players, rounded down
        num_cards = self.__num_decks * CARDS_PER_DECK
        indices = list(range(num_cards))
        random.shuffle(indices)  # Pre-shuffle indices it won't match card order
        suits = list(Suit)

        for i in range(num_cards):
            card_index = i % CARDS_PER_DECK
            suit_index = card_index // CARDS_PER_SUIT
            rank_index = card_index % CARDS_PER_SUIT + 1
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
        # Only active player can draw
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

    def bid(self, request: BidRequest) -> BidResponse | None:
        # Can only bid during draw or reserve (抓底牌) phases
        if self.__phase != GamePhase.DRAW and self.__phase != GamePhase.RESERVE:
            return None

        # Player must possess the cards
        if not self.__players[request.player_id].has_cards(request.cards):
            return None

        trump_type = self.__resolve_trump_type(request.cards)

        if self.__bidder_id != request.player_id:
            # If bidder is different from current bidder, trumps must be of a higher priority
            if trump_type <= self.__trump_type:
                return None
        else:
            # If bidder is same as current bidder, only allow fortify
            if (
                self.__trump_type != TrumpType.SINGLE
                or trump_type != TrumpType.SINGLE
                or self.__trump_suit != request.cards[0].suit
            ):
                return None
            trump_type = TrumpType.PAIR

        # Update states
        self.__trump_suit = request.cards[0].suit
        self.__trump_type = trump_type
        self.__bidder_id = request.player_id

        # In the first game, the bidder is the kitty player
        if self.__game_id == 0:
            self.__kitty_player_id = self.__bidder_id

        return BidResponse(self.__match_id, request.player_id, request.cards)

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
        self._kitty = request.cards

        # Update states
        self.__phase = GamePhase.PLAY
        self.__order.reset(self.__trump_suit)

        # Assign teams (fixed teams)
        num_players = len(self.__players)
        for offset in range(0, num_players, 2):
            self._defenders.add((self.__kitty_player_id + offset) % num_players)
        for offset in range(1, num_players, 2):
            self._attackers.add((self.__kitty_player_id + offset) % num_players)

        return KittyResponse(
            kitty_player.socket_id,
            request.player_id,
            self.__phase,
            request.cards,
            include_self=True,
        )

    def _end(self) -> None:
        self.__phase = GamePhase.END
        trick = self._tricks[-1]

        # Add kitty score
        if trick.winner_id in self._attackers:
            multiple = 2
            winner = trick.winning_play
            if len(winner.tractors) > 0:
                multiple = 2 ** (1 + max([len(t.pairs) for t in winner.tractors]))
            elif len(winner.pairs) > 0:
                multiple = 4
            self._score += multiple * sum([c.points for c in self._kitty])

        # Update level up players and resolve next lead player
        threshold = THRESHOLD_PER_DECK * self.__num_decks
        win_threshold = 2 * threshold
        if self._score >= win_threshold:
            # Attackers win
            levels = (self._score - win_threshold) // threshold
            self.next_lead_id = (self.__kitty_player_id + 1) % len(self.__players)
            for attacker in self._attackers:
                player = self.__players[attacker]
                # Bisect left: lowest level >= player's level
                max_level = BOSS_LEVELS[bisect_left(BOSS_LEVELS, player.level)]
                player.level = min(max_level, player.level + levels)
        else:
            # Defenders win
            score = self._score
            levels = (
                3 + (0 - score) // threshold
                if score <= 0
                else 2 if score < threshold else 1
            )
            self.next_lead_id = (self.__kitty_player_id + 2) % len(self.__players)
            for defender in self._defenders:
                player = self.__players[defender]
                # Bisect right: lowest level > player's level
                max_level = BOSS_LEVELS[bisect_right(BOSS_LEVELS, player.level)]
                player.level = min(max_level, player.level + levels)

    def play(self, request: PlayRequest) -> SocketResponse | None:
        # Only play during the play phase
        if self.__phase != GamePhase.PLAY:
            return []

        # Only active player can play
        if request.player_id != self.__active_player_id:
            return []

        # Create new trick if needed
        if len(self._tricks) == 0 or self._tricks[-1].ended:
            self._tricks.append(Trick(len(self.__players), self.__order))

        player = self.__players[request.player_id]
        other_players = [
            player for player in self.__players if player.id != request.player_id
        ]
        trick = self._tricks[-1]

        # Try processing play request
        if not trick.try_play(other_players, player, request.cards):
            return None

        # Play cards from player's hands
        player.play(request.cards)

        # Update play states
        self.__active_player_id = (self.__active_player_id + 1) % len(self.__players)
        response = PlayResponse(
            self.__match_id,
            request.player_id,
            self.__active_player_id,
            request.cards,
        )

        # Update trick states on end
        if trick.ended:
            if trick.winner_id in self._attackers:
                self._score += trick.score
            self.__active_player_id = trick.winner_id

            response = TrickResponse(
                self.__match_id, self._score, self.__active_player_id, response
            )

            # Update game states on end
            if not player.has_cards():
                self._end()

                response = EndResponse(
                    self.__match_id,
                    response,
                    self.__phase,
                    self.__kitty_player_id,
                    self._kitty,
                    self.next_lead_id,
                    self._score,
                )

        return response

    def ready(self, player_id: int) -> bool:
        if self.__players[player_id].level < END_LEVEL:
            self.__ready_players.add(player_id)
        return len(self.__ready_players) == len(self.__players)
