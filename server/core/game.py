import random
from bisect import bisect_left, bisect_right

from abstractions import Card, Cards, GamePhase, PlayerError, Room, Suit, TrumpType
from abstractions.events import CardsEvent, PlayerEvent
from abstractions.responses import (
    BidUpdate,
    DrawUpdate,
    EndUpdate,
    KittyUpdate,
    PlayUpdate,
    StartUpdate,
    TrickUpdate,
)
from core import Order, Player
from core.constants import BOSS_LEVELS, DECK_SIZE, DECK_THRESHOLD, KITTY_SIZE, SUIT_SIZE
from core.players import Players
from core.trick import Trick


class Game:
    def __init__(self, decks: int, players: Players, lead: int = -1, bid_team=False):
        if lead == -1:
            lead = players.first().pid

        # Inputs
        self.__decks = decks
        self.__players = players
        self.__bid_team = bid_team

        # Private
        self.__deck: list[Card] = []
        self.__bidder_pid = -1
        self.__trump_suit = Suit.UNKNOWN
        self.__trump_type = TrumpType.NONE
        self.__kitty_pid = lead
        self.__active_pid = lead
        self.__rank = self.__players[lead].level
        self.__order = Order(self.__rank)
        self.__ready_players: set[int] = set()

        # Protected for testing
        self._score = 0
        self._kitty: list[Card] = []
        self._tricks: list[Trick] = []
        self._attackers: set[int] = set()
        self._defenders: set[int] = set()

        # Public
        self.phase = GamePhase.DRAW
        self.next_pid = -1

        # Fix game rank for Aces game
        if self.__rank > SUIT_SIZE:
            self.__rank -= SUIT_SIZE

        # 1 deck for every 2 players, rounded down
        num_cards = self.__decks * DECK_SIZE
        indices = list(range(num_cards))
        random.shuffle(indices)  # Pre-shuffle indices it won't match card order
        suits = list(Suit)

        for i in range(num_cards):
            card_index = i % DECK_SIZE
            suit_index = card_index // SUIT_SIZE
            rank_index = card_index % SUIT_SIZE + 1
            self.__deck.append(Card(indices[i], suits[suit_index], rank_index))
        random.shuffle(self.__deck)

        self.__assign_teams()

    def __assign_teams(self) -> None:
        # Assign teams (fixed teams)
        pid = self.__kitty_pid
        self._defenders.clear()
        self._attackers.clear()
        for i in range(len(self.__players)):
            if i % 2 == 0:
                self._defenders.add(pid)
            else:
                self._attackers.add(pid)
            pid = self.__players.next(pid)

    def start(self) -> StartUpdate:
        return StartUpdate(
            self.__active_pid,
            self.__kitty_pid,
            self._attackers,
            self._defenders,
            len(self.__deck),
            self.__rank,
            self.phase,
        )

    def draw(self, event: PlayerEvent, room: Room) -> None:
        player = self.__players[event.pid]

        # Only active player can draw
        if event.pid != self.__active_pid:
            raise PlayerError("You can't draw", "It's not your turn.")

        if self.phase != GamePhase.DRAW and self.phase != GamePhase.RESERVE:
            raise PlayerError("You can't draw", "Not time to draw cards.")

        if self.phase == GamePhase.DRAW:
            # Draw card
            card = self.__deck.pop()
            player.draw([card])

            # Update states
            if len(self.__deck) == KITTY_SIZE:
                self.phase = GamePhase.RESERVE
                self.__active_pid = self.__kitty_pid
            else:
                self.__active_pid = self.__players.next(self.__active_pid)

            room.secret(
                "draw",
                DrawUpdate(player.pid, self.phase, self.__active_pid, [card]),
            )
        else:
            # Draw cards
            cards = self.__deck
            player.draw(cards)

            # Update states
            self.__deck = []
            self.phase = GamePhase.KITTY

            kitty_pid = self.__kitty_pid
            room.secret("draw", DrawUpdate(kitty_pid, self.phase, kitty_pid, cards))

    def __resolve_trump_type(self, cards: Cards) -> TrumpType:
        if len(cards) == 0 or len(cards) > 2:
            return TrumpType.NONE
        if len(cards) == 1:
            if cards[0].rank == self.__rank and cards[0].suit != Suit.JOKER:
                return TrumpType.SINGLE
            else:
                return TrumpType.NONE
        # Must be pairs
        if cards[0].suit != cards[1].suit or cards[0].rank != cards[1].rank:
            return TrumpType.NONE
        if cards[0].suit == Suit.JOKER:
            return TrumpType.BIG_JOKER if cards[0].rank == 2 else TrumpType.SMALL_JOKER
        if cards[0].rank == self.__rank:
            return TrumpType.PAIR

    def bid(self, event: CardsEvent, room: Room) -> None:
        player = self.__players[event.pid]

        # Can only bid during draw or reserve (抓底牌) phases
        if self.phase != GamePhase.DRAW and self.phase != GamePhase.RESERVE:
            raise PlayerError("Invalid bid", "Not time to bid.")

        # Player must possess the cards
        if not player.has_cards(event.cards):
            raise PlayerError("Invalid bid", "You don't have those cards.")

        trump_type = self.__resolve_trump_type(event.cards)

        # Player must possess the cards
        if trump_type == TrumpType.NONE:
            raise PlayerError("Invalid bid", "You must bid trump ranks or joker pairs.")

        if self.__bidder_pid != player.pid:
            # If bidder is different from current bidder, trumps must be of a higher priority
            if trump_type <= self.__trump_type:
                raise PlayerError("Invalid bid", "Your bid wasn't high enough.")
        else:
            # If bidder is same as current bidder, only allow fortify
            if (
                self.__trump_type != TrumpType.SINGLE
                or trump_type != TrumpType.SINGLE
                or self.__trump_suit != event.cards[0].suit
            ):
                raise PlayerError("Invalid bid", "You can only fortify your bid.")
            trump_type = TrumpType.PAIR

        # Update states
        self.__trump_suit = event.cards[0].suit
        self.__trump_type = trump_type
        self.__bidder_pid = player.pid

        if self.__bid_team:
            self.__kitty_pid = self.__bidder_pid
            self.__assign_teams()

        kitty_pid = self.__kitty_pid
        room.public(
            "bid",
            BidUpdate(
                player.pid, event.cards, kitty_pid, self._attackers, self._defenders
            ),
        )

    def kitty(self, event: CardsEvent, room: Room) -> None:
        player = self.__players[event.pid]

        # Only hide kitty during the kitty phase
        if self.phase != GamePhase.KITTY:
            raise PlayerError("Invalid kitty", "Not time to hide kitty.")

        # Only kitty player can hide kitty
        if event.pid != self.__kitty_pid:
            raise PlayerError("Invalid kitty", "It's not your turn.")

        # Number of cards must be correct
        if len(event.cards) != KITTY_SIZE:
            raise PlayerError("Invalid kitty", "Wrong number of cards.")

        # Player must possess the cards
        if not player.has_cards(event.cards):
            raise PlayerError("Invalid kitty", "You don't have those cards.")

        # Hide kitty
        player.play(event.cards)
        self._kitty = event.cards

        # Update states
        self.phase = GamePhase.PLAY
        self.__order.reset(self.__trump_suit)

        room.secret("kitty", KittyUpdate(event.pid, self.phase, event.cards))

    def _end(self) -> None:
        self.phase = GamePhase.END
        trick = self._tricks[-1]

        # Add kitty score
        if trick.winner_pid in self._attackers:
            multiple = 2
            winner = trick.winning_play
            if len(winner.tractors) > 0:
                multiple = 2 ** (1 + max([len(t.pairs) for t in winner.tractors]))
            elif len(winner.pairs) > 0:
                multiple = 4
            self._score += multiple * sum([c.points for c in self._kitty])

        # Update level up players and resolve next lead player
        threshold = DECK_THRESHOLD * self.__decks
        if self._score >= 2 * threshold:
            # Attackers win
            levels = (self._score - 2 * threshold) // threshold
            self.next_pid = self.__players.next(self.__kitty_pid)
            for attacker in self._attackers:
                player = self.__players[attacker]
                # Bisect left: lowest level >= player's level
                max_level = BOSS_LEVELS[bisect_left(BOSS_LEVELS, player.level)]
                player.level = min(max_level, player.level + levels)
        else:
            # Defenders win
            levels = (
                3 + (0 - self._score) // threshold
                if self._score <= 0
                else 2 if self._score < threshold else 1
            )
            self.next_pid = self.__players.next(self.__kitty_pid, 2)
            for defender in self._defenders:
                player = self.__players[defender]
                # Bisect right: lowest level > player's level
                max_level = BOSS_LEVELS[bisect_right(BOSS_LEVELS, player.level)]
                player.level = min(max_level, player.level + levels)

    def play(self, event: CardsEvent, room: Room) -> None:
        player = self.__players[event.pid]

        # Only play during the play phase
        if self.phase != GamePhase.PLAY:
            raise PlayerError("Invalid play", "Not time to play cards.")

        # Only active player can play
        if event.pid != self.__active_pid:
            raise PlayerError("Invalid play", "It's not your turn.")

        # Create new trick if needed
        if len(self._tricks) == 0 or self._tricks[-1].ended:
            self._tricks.append(Trick(len(self.__players), self.__order))

        # Process play event and play cards from player's hands
        player = self.__players[event.pid]
        trick = self._tricks[-1]
        trick.play(player, event.cards, room)

        # Update play states
        self.__active_pid = self.__players.next(self.__active_pid)
        update = PlayUpdate(event.pid, self.__active_pid, trick.winner_pid, event.cards)

        if not trick.ended:
            return room.public("play", update)

        # Update trick states on end
        if trick.winner_pid in self._attackers:
            self._score += trick.score
        self.__active_pid = trick.winner_pid

        update = TrickUpdate(update, self._score, self.__active_pid)
        if player.has_cards():
            return room.public("trick", update)

        # Update game states on end
        self._end()
        room.public(
            "end",
            EndUpdate(
                update,
                self.phase,
                self.__kitty_pid,
                self._kitty,
                self.next_pid,
                self._score,
                self.__players.updates(),
            ),
        )

    def ready(self, pid: int) -> bool:
        if self.__players[pid].level < BOSS_LEVELS[-1]:
            self.__ready_players.add(pid)
        return len(self.__ready_players) == len(self.__players)
