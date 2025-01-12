import random
from bisect import bisect_left, bisect_right

from abstractions import Card, Cards, GamePhase, PlayerError, Room, Suit, Trump
from abstractions.events import CardsEvent, PlayerEvent
from core import BOSS_LEVELS, DECK_SIZE, DECK_THRESHOLD, KITTY_SIZE, SUIT_SIZE, Order
from core.players import Players
from core.trick import Trick
from core.updates import (
    BidUpdate,
    DrawUpdate,
    EndUpdate,
    KittyUpdate,
    PlayUpdate,
    StartUpdate,
    TeamUpdate,
)


class Game:
    def __init__(
        self, decks: int, players: Players, room: Room, lead: int = -1, bid_team=False
    ):
        # Inputs
        self.__decks = decks
        self.__players = players
        self.__bid_team = bid_team

        # Private
        self.__deck: list[Card] = []
        self.__bidder_pid = -1
        self.__trump_suit = Suit.UNKNOWN
        self.__trump = Trump.NONE
        self.__kitty_pid = lead if lead != -1 else players.first().pid
        self.__active_pid = self.__kitty_pid
        self.__rank = self.__players[self.__kitty_pid].level
        self.__order = Order(self.__rank)
        self.__ready_players: set[int] = set()

        # Protected for testing
        self._score = 0
        self._kitty: list[Card] = []
        self._tricks: list[Trick] = []

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

        # Send updates to match room
        self.__players.assign_fixed_team(self.__kitty_pid)
        room.public(
            "start",
            StartUpdate(self.__active_pid, len(self.__deck), self.__rank),
        )
        room.public("team", TeamUpdate(self.__kitty_pid, self.__players.defenders()))

    def __ensure_valid_event(self, phase: GamePhase, pid: int | None = None) -> None:
        if phase != self.phase:
            raise PlayerError("Invalid action", "You can't do that right now.")
        if pid is not None and pid != self.__active_pid:
            raise PlayerError("Invalid action", "It's not your turn.")

    def draw(self, event: PlayerEvent, room: Room) -> None:
        self.__ensure_valid_event(GamePhase.DRAW, event.pid)

        # Draw cards
        player = self.__players[event.pid]
        count = 1 if len(self.__deck) > KITTY_SIZE else KITTY_SIZE
        cards = [self.__deck.pop() for _ in range(count)]
        player.draw(cards)

        # Update states
        if len(self.__deck) == 0:
            self.phase = GamePhase.KITTY
        elif len(self.__deck) == KITTY_SIZE:
            self.__active_pid = self.__kitty_pid
        else:
            self.__active_pid = self.__players.next(self.__active_pid)

        room.secret(
            "draw", DrawUpdate(player.pid, self.phase, self.__active_pid, cards)
        )

    def __resolve_trump(self, cards: Cards) -> Trump:
        if len(cards) == 0 or len(cards) > 2:
            return Trump.NONE
        rank, suit, level = cards[0].rank, cards[0].suit, self.__rank
        if len(cards) == 1:
            return Trump.SINGLE if rank == level and suit != Suit.JOKER else Trump.NONE
        # Must be pairs
        if suit != cards[1].suit or rank != cards[1].rank:
            return Trump.NONE
        if suit == Suit.JOKER:
            return Trump.BIG_JOKER if rank == 2 else Trump.SMALL_JOKER
        if rank == level:
            return Trump.PAIR

    def bid(self, event: CardsEvent, room: Room) -> None:
        self.__ensure_valid_event(GamePhase.DRAW)
        trump = self.__resolve_trump(event.cards)

        # Player must possess the cards
        if trump == Trump.NONE:
            raise PlayerError("Invalid bid", "You must bid trump ranks or joker pairs.")

        pid = self.__players[event.pid].pid
        if self.__bidder_pid != pid:
            # If bidder is different from current bidder, trumps must be of a higher priority
            if trump <= self.__trump:
                raise PlayerError("Invalid bid", "Your bid wasn't high enough.")
        else:
            # If bidder is same as current bidder, only allow fortify
            if (
                self.__trump != Trump.SINGLE
                or trump != Trump.SINGLE
                or self.__trump_suit != event.cards[0].suit
            ):
                raise PlayerError("Invalid bid", "You can only fortify your bid.")
            trump = Trump.PAIR

        # Update states
        self.__trump_suit = event.cards[0].suit
        self.__trump = trump
        self.__bidder_pid = pid

        if self.__bid_team:
            self.__kitty_pid = pid
            self.__players.assign_fixed_team(pid)
            room.public("team", TeamUpdate(pid, self.__players.defenders()))

        kitty_pid = self.__kitty_pid
        room.public("bid", BidUpdate(pid, event.cards, kitty_pid))

    def kitty(self, event: CardsEvent, room: Room) -> None:
        self.__ensure_valid_event(GamePhase.KITTY, event.pid)

        # Number of cards must be correct
        if len(event.cards) != KITTY_SIZE:
            raise PlayerError("Invalid kitty", "Wrong number of cards.")

        # Hide kitty
        self.__players[event.pid].play(event.cards)
        self._kitty = event.cards

        # Update states
        self.phase = GamePhase.PLAY
        self.__order.reset(self.__trump_suit)

        room.secret("kitty", KittyUpdate(event.pid, self.phase, event.cards))

    # Return final kitty play update
    def _end(self) -> PlayUpdate:
        self.phase = GamePhase.END
        kitty_pid = self.__kitty_pid

        # Add kitty score
        if (trick := self._tricks[-1]).winner_pid in self.__players.attackers():
            multiple = 2
            winner = trick.winning_play
            if len(winner.tractors) > 0:
                multiple = 2 ** (1 + max([len(t.pairs) for t in winner.tractors]))
            elif len(winner.pairs) > 0:
                multiple = 4
            self._score += multiple * sum([c.points for c in self._kitty])

        # Update level up players and resolve next lead player
        if self._score >= 2 * (threshold := DECK_THRESHOLD * self.__decks):
            # Attackers win
            levels = (self._score - 2 * threshold) // threshold
            self.next_pid = self.__players.next(kitty_pid)
            for attacker in self.__players.attackers():
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
            self.next_pid = self.__players.next(kitty_pid, 2)
            for defender in self.__players.defenders():
                player = self.__players[defender]
                # Bisect right: lowest level > player's level
                max_level = BOSS_LEVELS[bisect_right(BOSS_LEVELS, player.level)]
                player.level = min(max_level, player.level + levels)

        return PlayUpdate(kitty_pid, self.next_pid, self._kitty, score=self._score)

    def play(self, event: CardsEvent, room: Room) -> None:
        self.__ensure_valid_event(GamePhase.PLAY, event.pid)

        # Create new trick if needed
        if len(self._tricks) == 0 or self._tricks[-1].ended:
            self._tricks.append(Trick(len(self.__players), self.__order))

        # Process play event and play cards from player's hands
        player = self.__players[event.pid]
        trick = self._tricks[-1]
        trick.play(player, event.cards)

        # Update play states
        self.__active_pid = self.__players.next(self.__active_pid)
        update = PlayUpdate(event.pid, self.__active_pid, event.cards, trick.winner_pid)

        if not trick.ended:
            return room.public("play", update)

        # Update play states if trick ended
        if trick.winner_pid in self.__players.attackers():
            self._score += trick.score
        update.score = self._score
        update.active_pid = self.__active_pid = trick.winner_pid

        if player.has_cards():
            return room.public("play", update)

        # Update game states on end
        room.public("end", EndUpdate(update, self._end(), self.__players.infos()))

    def ready(self, pid: int) -> bool:
        self.__ensure_valid_event(GamePhase.END)
        if self.__players[pid].level < BOSS_LEVELS[-1]:
            self.__ready_players.add(pid)
        return len(self.__ready_players) == len(self.__players)
