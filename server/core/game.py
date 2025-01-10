import random
from bisect import bisect_left, bisect_right
from typing import List, Sequence, Set
from abstractions import Card, GamePhase, Room, Suit, TrumpType
from abstractions.constants import BOSS_LEVELS, DECK_SIZE, SUIT_SIZE, THRESHOLD_PER_DECK
from abstractions.events import CardsEvent, PlayerEvent
from abstractions.responses import (
    AlertUpdate,
    DrawUpdate,
    EndUpdate,
    PlayUpdate,
    StartUpdate,
    KittyUpdate,
    TrickUpdate,
    BidUpdate,
)
from core import Order, Player
from core.trick import Trick


class Game:
    def __init__(
        self,
        game_id,
        num_decks: int,
        players: Sequence[Player],
        lead_player_id: int | None = None,
    ) -> None:
        if lead_player_id is None:
            lead_player_id = players[0].id

        # Inputs
        self.__game_id = game_id
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
        if self.__game_rank > SUIT_SIZE:
            self.__game_rank -= SUIT_SIZE

        # 1 deck for every 2 players, rounded down
        num_cards = self.__num_decks * DECK_SIZE
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
        player_id = self.__kitty_player_id
        self._defenders.clear()
        self._attackers.clear()
        for i in range(len(self.__players)):
            if i % 2 == 0:
                self._defenders.add(player_id)
            else:
                self._attackers.add(player_id)
            player_id = self.__next_player_id(player_id)

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

    def start(self) -> StartUpdate:
        return StartUpdate(
            self.__active_player_id,
            self.__kitty_player_id,
            self._attackers,
            self._defenders,
            len(self.__deck),
            self.__game_rank,
            self.phase,
        )

    def draw(self, event: PlayerEvent, room: Room) -> None:
        player = self.__player_for_id(event.player_id)

        # Only active player can draw
        if event.player_id != self.__active_player_id:
            room.reply("alert", AlertUpdate("You can't draw", "It's not your turn."))
        elif self.phase == GamePhase.DRAW:
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

            room.secret(
                "draw",
                DrawUpdate(player.id, self.phase, self.__active_player_id, [card]),
            )
        elif self.phase == GamePhase.RESERVE:
            # Draw cards
            cards = self.__deck
            player.draw(cards)

            # Update states
            self.__deck = []
            self.phase = GamePhase.KITTY

            kitty_id = self.__kitty_player_id
            room.secret("draw", DrawUpdate(kitty_id, self.phase, kitty_id, cards))
        else:
            room.reply(
                "alert", AlertUpdate("You can't draw", "Not time to draw cards.")
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

    def bid(self, event: CardsEvent, room: Room) -> None:
        player = self.__player_for_id(event.player_id)

        # Can only bid during draw or reserve (抓底牌) phases
        if self.phase != GamePhase.DRAW and self.phase != GamePhase.RESERVE:
            room.reply("alert", AlertUpdate("Invalid bid", "Not time to bid."))
            return

        # Player must possess the cards
        if not player.has_cards(event.cards):
            room.reply(
                "alert", AlertUpdate("Invalid bid", "You don't have those cards.")
            )
            return

        trump_type = self.__resolve_trump_type(event.cards)

        # Player must possess the cards
        if trump_type == TrumpType.NONE:
            room.reply(
                "alert",
                AlertUpdate("Invalid bid", "You must bid with trump ranks or jokers."),
            )
            return

        if self.__bidder_id != player.id:
            # If bidder is different from current bidder, trumps must be of a higher priority
            if trump_type <= self.__trump_type:
                room.reply(
                    "alert", AlertUpdate("Invalid bid", "Your bid wasn't high enough.")
                )
                return
        else:
            # If bidder is same as current bidder, only allow fortify
            if (
                self.__trump_type != TrumpType.SINGLE
                or trump_type != TrumpType.SINGLE
                or self.__trump_suit != event.cards[0].suit
            ):
                room.reply(
                    "alert",
                    AlertUpdate(
                        "Invalid bid", "You can only fortify your current bid."
                    ),
                )
                return
            trump_type = TrumpType.PAIR

        # Update states
        self.__trump_suit = event.cards[0].suit
        self.__trump_type = trump_type
        self.__bidder_id = player.id

        # In the first game, the bidder is the kitty player
        if self.__game_id == 0:
            self.__kitty_player_id = self.__bidder_id
            self.__assign_teams()

        kitty_id = self.__kitty_player_id
        room.public(
            "bid",
            BidUpdate(
                player.id, event.cards, kitty_id, self._attackers, self._defenders
            ),
        )

    def kitty(self, event: CardsEvent, room: Room) -> None:
        player = self.__player_for_id(event.player_id)

        # Only hide kitty during the kitty phase
        if self.phase != GamePhase.KITTY:
            room.reply("alert", AlertUpdate("Invalid kitty", "Not time to hide kitty."))
            return

        # Only kitty player can hide kitty
        if event.player_id != self.__kitty_player_id:
            room.reply("alert", AlertUpdate("Invalid kitty", "It's not your turn."))
            return

        # Number of cards must be correct
        if len(event.cards) != 8:
            room.reply("alert", AlertUpdate("Invalid kitty", "Wrong number of cards."))
            return

        # Player must possess the cards
        if not player.has_cards(event.cards):
            room.reply(
                "alert", AlertUpdate("Invalid kitty", "You don't have those cards.")
            )
            return

        # Hide kitty
        player.play(event.cards)
        self._kitty = event.cards

        # Update states
        self.phase = GamePhase.PLAY
        self.__order.reset(self.__trump_suit)

        room.secret("kitty", KittyUpdate(event.player_id, self.phase, event.cards))

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

    def play(self, event: CardsEvent, room: Room) -> None:
        player = self.__player_for_id(event.player_id)

        # Only play during the play phase
        if self.phase != GamePhase.PLAY:
            room.reply("alert", AlertUpdate("Invalid play", "Not time to play cards."))
            return

        # Only active player can play
        if event.player_id != self.__active_player_id:
            room.reply("alert", AlertUpdate("Invalid play", "It's not your turn."))
            return

        # Create new trick if needed
        if len(self._tricks) == 0 or self._tricks[-1].ended:
            self._tricks.append(Trick(len(self.__players), self.__order))

        player = self.__player_for_id(event.player_id)
        other_players = [
            player for player in self.__players if player.id != event.player_id
        ]
        trick = self._tricks[-1]

        # Try processing play event
        if not trick.try_play(other_players, player, event.cards, room):
            return

        # Play cards from player's hands
        player.play(event.cards)

        # Update play states
        self.__active_player_id = self.__next_player_id(self.__active_player_id)
        update = PlayUpdate(
            event.player_id, self.__active_player_id, trick.winner_id, event.cards
        )

        if not trick.ended:
            room.public("play", update)
            return

        # Update trick states on end
        if trick.winner_id in self._attackers:
            self._score += trick.score
        self.__active_player_id = trick.winner_id

        update = TrickUpdate(update, self._score, self.__active_player_id)
        if player.has_cards():
            room.public("trick", update)
            return

        # Update game states on end
        self._end()
        room.public(
            "end",
            EndUpdate(
                update,
                self.phase,
                self.__kitty_player_id,
                self._kitty,
                self.next_lead_id,
                self._score,
                [(player.id, player.level) for player in self.__players],
            ),
        )

    def ready(self, player_id: int) -> bool:
        if self.__player_for_id(player_id).level < BOSS_LEVELS[-1]:
            self.__ready_players.add(player_id)
        return len(self.__ready_players) == len(self.__players)
