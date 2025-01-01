import random
from bisect import bisect_left, bisect_right
from typing import List, Sequence, Set
from abstractions import Card, GamePhase, Suit, TrumpType
from abstractions.constants import (
    BOSS_LEVELS,
    CARDS_PER_DECK,
    CARDS_PER_SUIT,
    END_LEVEL,
    THRESHOLD_PER_DECK,
)
from abstractions.requests import DrawRequest, KittyRequest, PlayRequest, BidRequest
from abstractions.responses import (
    AlertResponse,
    DrawResponse,
    EndResponse,
    PlayResponse,
    SocketResponse,
    StartResponse,
    KittyResponse,
    TrickResponse,
    BidResponse,
)
from core import Order, Player
from core.trick import Trick


class Game:
    def __init__(
        self,
        game_id,
        match_id: int,
        num_decks: int,
        players: Sequence[Player],
        lead_player_id: int | None = None,
    ) -> None:
        if lead_player_id is None:
            lead_player_id = players[0].id

        # Inputs
        self.__game_id = game_id
        self.__match_id = match_id
        self.__num_decks = num_decks
        self.__players = players

        # Private
        self.__deck: List[Card] = []
        self.__bidder_id = -1
        self.__trump_suit = Suit.UNKNOWN
        self.__trump_type = TrumpType.NONE
        self.__kitty_player_id = lead_player_id
        self.__active_player_id = lead_player_id
        self.__game_rank = self.__player_for_id(lead_player_id).level
        self.__order = Order(self.__game_rank)
        self.__ready_players: Set[int] = set()

        # Protected for testing
        self._score = 0
        self._kitty: List[Card] = []
        self._tricks: List[Trick] = []
        self._attackers: Set[int] = set()
        self._defenders: Set[int] = set()

        # Public
        self.phase = GamePhase.DRAW
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

    def __next_player_id(self, player_id: int, increment: int = 1) -> int:
        player_index = -1
        for index, player in enumerate(self.__players):
            if player.id == player_id:
                player_index = index

        next_index = (player_index + increment) % len(self.__players)
        return self.__players[next_index].id

    def __player_for_id(self, player_id: int) -> Player:
        for player in self.__players:
            if player.id == player_id:
                return player
        raise RuntimeError(f"Cannot find player with id {player_id}")

    def start(self) -> StartResponse:
        return StartResponse(
            self.__match_id,
            self.__active_player_id,
            len(self.__deck),
            self.__game_rank,
            self.phase,
        )

    def draw(self, request: DrawRequest) -> SocketResponse:
        player = self.__player_for_id(request.player_id)
        socket_id = player.socket_id

        # Only active player can draw
        if request.player_id != self.__active_player_id:
            return AlertResponse(socket_id, "You can't draw", "It's not your turn.")

        if self.phase == GamePhase.DRAW:
            # Draw card
            card = self.__deck.pop()
            player.draw([card])

            # Update states
            if len(self.__deck) == 8:
                self.phase = GamePhase.RESERVE
                self.__active_player_id = self.__kitty_player_id
            else:
                self.__active_player_id = self.__next_player_id(self.__active_player_id)
                print(f"Next player: {self.__active_player_id}")

            return DrawResponse(
                socket_id,
                player.id,
                self.phase,
                self.__active_player_id,
                [card],
                include_self=True,
            )

        elif self.phase == GamePhase.RESERVE:
            # Draw cards
            cards = self.__deck
            player.draw(cards)

            # Update states
            self.__deck = []
            self.phase = GamePhase.KITTY

            return DrawResponse(
                socket_id,
                self.__kitty_player_id,
                self.phase,
                self.__kitty_player_id,
                cards,
                include_self=True,
            )

        return AlertResponse(socket_id, "You can't draw", "Not time to draw cards.")

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

    def bid(self, request: BidRequest) -> SocketResponse:
        player = self.__player_for_id(request.player_id)
        socket_id = player.socket_id

        # Can only bid during draw or reserve (抓底牌) phases
        if self.phase != GamePhase.DRAW and self.phase != GamePhase.RESERVE:
            return AlertResponse(socket_id, "Invalid bid", "Not time to bid.")

        # Player must possess the cards
        if not player.has_cards(request.cards):
            return AlertResponse(
                socket_id, "Invalid bid", "You don't have those cards."
            )

        trump_type = self.__resolve_trump_type(request.cards)

        # Player must possess the cards
        if trump_type == TrumpType.NONE:
            return AlertResponse(
                socket_id, "Invalid bid", "You must bid with trump ranks or jokers."
            )

        if self.__bidder_id != player.id:
            # If bidder is different from current bidder, trumps must be of a higher priority
            if trump_type <= self.__trump_type:
                return AlertResponse(
                    socket_id, "Invalid bid", "Your bid wasn't high enough."
                )
        else:
            # If bidder is same as current bidder, only allow fortify
            if (
                self.__trump_type != TrumpType.SINGLE
                or trump_type != TrumpType.SINGLE
                or self.__trump_suit != request.cards[0].suit
            ):
                return AlertResponse(
                    socket_id, "Invalid bid", "You can only fortify your current bid."
                )
            trump_type = TrumpType.PAIR

        # Update states
        self.__trump_suit = request.cards[0].suit
        self.__trump_type = trump_type
        self.__bidder_id = player.id

        # In the first game, the bidder is the kitty player
        if self.__game_id == 0:
            self.__kitty_player_id = self.__bidder_id

        return BidResponse(self.__match_id, player.id, request.cards)

    def kitty(self, request: KittyRequest) -> SocketResponse:
        player = self.__player_for_id(request.player_id)
        socket_id = player.socket_id

        # Only hide kitty during the kitty phase
        if self.phase != GamePhase.KITTY:
            return AlertResponse(socket_id, "Invalid kitty", "Not time to hide kitty.")

        # Only kitty player can hide kitty
        if request.player_id != self.__kitty_player_id:
            return AlertResponse(socket_id, "Invalid kitty", "It's not your turn.")

        # Number of cards must be correct
        if len(request.cards) != 8:
            return AlertResponse(socket_id, "Invalid kitty", "Wrong number of cards.")

        # Player must possess the cards
        if not player.has_cards(request.cards):
            return AlertResponse(
                socket_id, "Invalid kitty", "You don't have those cards."
            )

        # Hide kitty
        player.play(request.cards)
        self._kitty = request.cards

        # Update states
        self.phase = GamePhase.PLAY
        self.__order.reset(self.__trump_suit)

        # Assign teams (fixed teams)
        player_id = self.__kitty_player_id
        for i in range(len(self.__players)):
            if i % 2 == 0:
                self._defenders.add(player_id)
            else:
                self._attackers.add(player_id)
            player_id = self.__next_player_id(player_id)

        return KittyResponse(
            socket_id,
            request.player_id,
            self.phase,
            request.cards,
            include_self=True,
        )

    def _end(self) -> None:
        self.phase = GamePhase.END
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
            self.next_lead_id = self.__next_player_id(self.__kitty_player_id)
            for attacker in self._attackers:
                player = self.__player_for_id(attacker)
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
            self.next_lead_id = self.__next_player_id(self.__kitty_player_id, 2)
            for defender in self._defenders:
                player = self.__player_for_id(defender)
                # Bisect right: lowest level > player's level
                max_level = BOSS_LEVELS[bisect_right(BOSS_LEVELS, player.level)]
                player.level = min(max_level, player.level + levels)

    def play(self, request: PlayRequest) -> SocketResponse:
        player = self.__player_for_id(request.player_id)
        socket_id = player.socket_id

        # Only play during the play phase
        if self.phase != GamePhase.PLAY:
            return AlertResponse(socket_id, "Invalid play", "Not time to play cards.")

        # Only active player can play
        if request.player_id != self.__active_player_id:
            return AlertResponse(socket_id, "Invalid play", "It's not your turn.")

        # Create new trick if needed
        if len(self._tricks) == 0 or self._tricks[-1].ended:
            self._tricks.append(Trick(len(self.__players), self.__order))

        player = self.__player_for_id(request.player_id)
        other_players = [
            player for player in self.__players if player.id != request.player_id
        ]
        trick = self._tricks[-1]

        # Try processing play request
        alert = trick.try_play(other_players, player, request.cards)
        if alert is not None:
            return alert

        # Play cards from player's hands
        player.play(request.cards)

        # Update play states
        self.__active_player_id = self.__next_player_id(self.__active_player_id)
        response = PlayResponse(
            self.__match_id,
            request.player_id,
            self.__active_player_id,
            trick.winner_id,
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
                    self.phase,
                    self.__kitty_player_id,
                    self._kitty,
                    self.next_lead_id,
                    self._score,
                )

        return response

    def ready(self, player_id: int) -> bool:
        if self.__player_for_id(player_id).level < END_LEVEL:
            self.__ready_players.add(player_id)
        return len(self.__ready_players) == len(self.__players)
