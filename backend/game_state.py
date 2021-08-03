from __future__ import annotations
import logging
import random
import time
from enum import IntEnum
from threading import RLock, Semaphore
from collections import deque
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    Sequence,
    Tuple)
from shengji_pb2 import (
    Card as CardProto,
    Game as GameProto,
    Player as PlayerProto)

# Type aliases
GameState = GameProto.GameState
Suit = CardProto.Suit
Rank = CardProto.Rank

# Utility functions
def getCardNum(card: CardProto) -> int:
    return card.suit * 100 + card.rank

def toCardProto(cardNum: int) -> CardProto:
    return CardProto(suit = cardNum // 100, rank = cardNum % 100)

class TrumpType(IntEnum):
    INVALID = 0
    NONE = 1
    SINGLE = 2
    PAIR = 3
    SMALL_JOKER = 4
    BIG_JOKER = 5


# Functional ranking
class Ranking:
    def __init__(self, rank: int) -> None:
        self.trumpRank: int = rank
        self.trumpSuit: Suit = Suit.SUIT_UNDEFINED
        self.__ranking: Dict[CardProto, int] = dict()
        self.resetOrder(self.trumpSuit)

    def resetOrder(self, suit: Suit):
        self.trumpSuit = suit
        nonTrumpSuits = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS].remove(suit)
        ranking = 0

        # Jokers
        self.__ranking[CardProto(suit=Suit.BIG_JOKER, rank=Rank.RANK_UNDEFINED)] = ranking
        ranking += 1
        self.__ranking[CardProto(suit=Suit.SMALL_JOKER, rank=Rank.RANK_UNDEFINED)] = ranking
        ranking += 1

        # Trump suit + rank
        if self.trumpSuit != Suit.SUIT_UNDEFINED \
            and self.trumpSuit != Suit.BIG_JOKER \
            and self.trumpSuit != Suit.SMALL_JOKER:
                self.__ranking[CardProto(suit=self.trumpSuit, rank=self.trumpRank)] = ranking
                ranking += 1

        # Trump rank
        for suit in nonTrumpSuits:
            self.__ranking[CardProto(suit=suit, rank=self.trumpRank)] = ranking
        ranking += 1

        # Trump suit
        if self.trumpSuit != Suit.SUIT_UNDEFINED \
            and self.trumpSuit != Suit.BIG_JOKER \
            and self.trumpSuit != Suit.SMALL_JOKER:
                for rank in range(Rank.KING, Rank.TWO, -1):
                    if rank != self.trumpRank:
                        self.__ranking[CardProto(suit=self.trumpSuit, rank=self.trumpRank)] = ranking
                        ranking += 1

        # Others
        for rank in range(Rank.KING, Rank.TWO, -1):
            if rank != self.trumpRank:
                for suit in nonTrumpSuits:
                    self.__ranking[CardProto(suit=suit, rank=self.trumpRank)] = ranking
                ranking += 1

    # For trick resolution
    def getRank(self, card: CardProto) -> int:
        return self.__ranking[str(card)]

    def isTrump(self, card: CardProto) -> bool:
        return card.suit == Suit.BIG_JOKER \
            or card.suit == Suit.SMALL_JOKER \
            or card.rank == self.trumpRank \
            or (card.suit == self.trumpSuit \
                and self.trumpSuit != Suit.SUIT_UNDEFINED)


class Tractor:
    def __init__(self, card: CardProto, length: int) -> None:
        self.card: CardProto = card
        self.length: int = length

    def __str__(self) -> str:
        return f'{self.card}:{self.length}'

class TrickFormat:
    def __init__(self, suit: Suit, length: int, isTrump: bool) -> None:
        self.suit = suit
        self.length = length
        self.isTrump = isTrump
        self.tractors: List[Tractor] = []
        self.pairs: List[CardProto] = []
        self.singles: List[CardProto] = []

    """
        TODO: Greedy isn't completely accurate, DP is likely necessary
        For example, tractors [3, 2, 2] is satisfied by [4, 3] but not vice versa
        Currently, exact format is required
    """
    def verify(self, format: TrickFormat) -> bool:
        if len(self.tractors) != len(format.tractors):
            logging.info('Number of tractors do not match')
            return False

        self.tractors.sort(key = lambda t: t.length)
        format.tractors.sort(key = lambda t: t.length)

        for selfTractor, formatTractor in zip(self.tractors, format.tractors):
            if selfTractor.length != formatTractor.length:
                logging.info('Tractors lengths do not match')
                return False

        if len(self.pairs) != len(format.pairs):
            logging.info('Number of pairs do not match')
            return False

        if len(self.singles) != len(format.singles):
            logging.info('Number of singles do not match')
            return False

        return True

    def __str__(self) -> str:
        if self.length == 0:
            return 'Invalid format'
        if self.suit == Suit.SUIT_UNDEFINED:
            return 'Mixed format'

        format = 'Suit: ' + self.suit
        format += '\nTractor: '
        for tractor in self.tractors:
            format += f'{tractor}, '
        format += '\nPairs: '
        for pair in self.pairs:
            format += f'{pair}, '
        format += '\Singles: '
        for single in self.singles:
            format += f'{single}, '
        return format

class Trick:
    def __init__(self, game: Game) -> None:
        self.__game = game


class Player:
    def __init__(self, player_name: str, notify: bool) -> None:
        self.player_name: str = player_name
        self.__notify: bool = notify
        self.__game_queue: deque[GameProto]  = deque()
        self.__game_queue_sem: Semaphore= Semaphore(0)
        self.cards_on_hand: Dict[CardProto, int] = dict()

    def can_play_cards(self, cards: Sequence[CardProto]) -> bool:
        card_as_dict = dict()
        for card in cards:
            hashable_card = getCardNum(card)
            card_as_dict[hashable_card] = card_as_dict.get(hashable_card, 0) + 1
        for key in card_as_dict:
            if card_as_dict.get(key, 0) > self.cards_on_hand.get(key, 0):
                return False
        return True

    def remove_card(self, card: CardProto) -> None:
        hashable_card = getCardNum(card)
        self.cards_on_hand[hashable_card] = max(0, self.cards_on_hand[hashable_card] - 1)
        if self.cards_on_hand[hashable_card] == 0:
            del self.cards_on_hand[hashable_card]

    def add_card(self, card: CardProto) -> None:
        hashable_card = getCardNum(card)
        self.cards_on_hand[hashable_card] = self.cards_on_hand.get(hashable_card, 0) + 1

    def queue_update(self, game: GameProto) -> None:
        if self.__notify:
            self.__game_queue.append(game)
            self.__game_queue_sem.release()

    def complete_update_stream(self) -> None:
        self.__notify = False
        self.__game_queue_sem.release()

    def update_stream(self) -> Iterable[GameProto]:
        while True:
            self.__game_queue_sem.acquire()
            if self.__notify == False:
                break
            game_proto = self.__game_queue.popleft()
            yield game_proto

    def to_player_proto(self) -> PlayerProto:
        player_proto = PlayerProto()
        player_proto.player_name = self.player_name
        for card,count in self.cards_on_hand.items():
            for _ in range(count):
                player_proto.cards_on_hand.cards.append(toCardProto(card))
        return player_proto


class Game:
    def __init__(self, creator_name: str, game_id: str, delay: float) -> None:
        self.state: GameState = GameState.AWAIT_JOIN
        self.__game_id: str = game_id
        self.__creator_name: str = creator_name
        self.__kitty_player_name: str = creator_name
        self.__delay: float = delay
        self.__players: Dict[str, Player] = dict()
        self.__players_lock: RLock = RLock()
        self._next_player_name: str = creator_name
        self.__kitty: List[CardProto] = []
        self.__update_id: int = 0
        self.__update_lock: RLock = RLock()
        # hands on table contains an array of pairs - (id, hand)
        self.__action_count: int = 0
        self.__hands_on_table: List[tuple[str, Hand]] = []
        self.__current_rank: Rank = Rank.TWO
        self.__trump_declarer: str = ''
        self.__current_trump_cards: Sequence[CardProto] = []
        self.__play_order: Sequence[str] = []

        # shuffle two decks of cards
        self.__deck_cards: List[CardProto] = []
        for i in range(2):
            self.__deck_cards.append(CardProto(suit=Suit.BIG_JOKER,rank=Rank.RANK_UNDEFINED))
            self.__deck_cards.append(CardProto(suit=Suit.SMALL_JOKER,rank=Rank.RANK_UNDEFINED))
            for s in Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS:
                for r in range(Rank.ACE, Rank.KING + 1):
                    self.__deck_cards.append(CardProto(suit=s,rank=r))

        random.shuffle(self.__deck_cards)

    def get_trump_type(self, cards: Sequence[CardProto]) -> TrumpType:
        if len(cards) == 0:
            return TrumpType.NONE
        if len(cards) == 1 and cards[0].rank == self.__current_rank:
            return TrumpType.SINGLE
        if len(cards) == 2:
            if cards[0].suit == Suit.SMALL_JOKER and cards[1].suit == Suit.SMALL_JOKER:
                return TrumpType.SMALL_JOKER
            if cards[0].suit == Suit.BIG_JOKER and cards[1].suit == Suit.BIG_JOKER:
                return TrumpType.BIG_JOKER
            if cards[0].suit == cards[1].suit and cards[0].rank == cards[1].rank == self.__current_rank:
                return TrumpType.PAIR
        return TrumpType.INVALID

    def add_player(self, player_name: str, notify: bool) -> Player:
        with self.__players_lock:
            if player_name in self.__players.keys() or len(self.__players) == 4:
                return None
            player = Player(player_name, notify)
            self.__players[player_name] = player

            if len(self.__players) == 4:
                self.state = GameState.AWAIT_DEAL

            self.__new_player_update(player_name)
        self.__play_order.append(player_name)

        return player

    def complete_player_stream(self) -> None:
        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            player.complete_update_stream()

    def play(self, player_name: str, cards: Sequence[CardProto]) -> Tuple[bool, str]:
        logging.info(f'{player_name} plays {cards} at state: {self.state}')
        if player_name != self._next_player_name and self.state != GameState.DEAL and self.state != GameState.AWAIT_TRUMP_DECLARATION:
            return False, f'Not the turn of player {player_name}. Next player: {self._next_player_name}'
        if self.__can_declare_trump():
            return self.__declare_trump(self.__players[player_name], cards)

        if (self.state == GameState.HIDE_KITTY):
            return self.__hide_kitty(self.__players[player_name], cards)

        if (self.state == GameState.PLAY):
            if not self.__players[player_name].can_play_cards(cards):
                return False, f'Player does not possess the cards: {cards}'
            self.__hands_on_table.append(Hand(cards))
            self._next_player_name = self.__play_order[(self.__play_order.index(player_name) + 1) % 4]
            round_winner = None
            if len(self.__hands_on_table) == 4:
                round_winner= random.choice(list(self.__players.keys()))
                self._next_player_name = round_winner
                self.__hands_on_table = []
            player = self.__players[player_name]
            for card in cards:
                player.remove_card(card)
            self.__trick_played_update(player_name, cards)
            return True, ''

        # TODO: Update players if play is valid

        # Check validity
        hand = Hand(cards)

        # Check play cards
        prev_hand = None
        if len(self.__hands_on_table) > 0:
            prev_hand = self.__hands_on_table[0][1]

        if not self.players[player_name].CanPlayHand(hand, prev_hand, self.__metadata):
            return False, 'Invalid hand'

        # play this hand and update cards on table
        self.hands_on_table.append((player_name, hand))
        self.__players[player_name].PlayHand(hand)

        # Compute winner of this round if needed
        if len(self.__hands_on_table) == 4:
            self._next_player_name = GetWinnerAndAccumulateScore()
        else:
            self._next_player_name = self.NextPlayer()

        # Check to see if the game has ended
        self.__action_count += 1
        return True, ''

    def drawCards(self, player_name: str) -> None:
        if self.state == GameState.AWAIT_DEAL and player_name == self.__creator_name:
            self.__deal_hands()
        elif self.state == GameState.AWAIT_TRUMP_DECLARATION and player_name == self.__kitty_player_name:
            self.state = GameState.DEAL_KITTY
            self.__deal_kitty()
            self._next_player_name = self.__kitty_player_name

    def to_game_proto(self, increment_update_id: bool = True) -> GameProto:
        with self.__update_lock:
            update_id = self.__update_id
            if increment_update_id:
                self.__update_id += 1

        game = GameProto()
        game.update_id = update_id
        game.game_id = self.__game_id
        game.creator_player_name = self.__creator_name

        game.current_rank = self.__current_rank
        game.trump_player_name = self.__trump_declarer
        game.next_turn_player_name = self._next_player_name
        game.trump_cards.cards.extend(self.__current_trump_cards)

        game.kitty_player_name = self.__kitty_player_name
        game.state = self.state

        with self.__players_lock:
            players = self.__players.values()
        game.players.extend([p.to_player_proto() for p in players])

        game.kitty.cards.extend(self.__kitty)

        return game

    def __deal_hands(self) -> None:
        self.state = GameState.DEAL
        with self.__players_lock:
            players = list(self.__players.values())

        deal_index = 0

        while (len(self.__deck_cards) > 8):
            player = players[deal_index]
            card = self.__deck_cards.pop()
            player.add_card(card)
            logging.info(f'Dealt card {card} to {player.player_name}')
            deal_index = (deal_index + 1) % 4

            if len(self.__deck_cards) == 8:
                self.state = GameState.AWAIT_TRUMP_DECLARATION

            time.sleep(self.__delay)
            self.__card_dealt_update(player.player_name, card)

    def __deal_kitty(self) -> None:
        while (len(self.__deck_cards) > 0):
            player = self.__players[self.__kitty_player_name]
            card = self.__deck_cards.pop()
            player.add_card(card)
            logging.info(f'Dealt kitty card {card} to {player.player_name}')

            if len(self.__deck_cards) == 0:
                self.state = GameState.HIDE_KITTY

            time.sleep(self.__delay)
            self.__card_dealt_update(player.player_name, card)

    def __can_declare_trump(self) -> bool:
        return self.state == GameState.DEAL or self.state == GameState.AWAIT_TRUMP_DECLARATION

    def __declare_trump(self, player: Player, cards: Sequence[CardProto]) -> Tuple[bool, str]:
        logging.info(f'{player} declares trump as: {cards}')

        if not player.can_play_cards(cards):
            return False, f'Player does not possess the cards: {cards}'

        current_trump_type = self.get_trump_type(self.__current_trump_cards)
        assert current_trump_type != TrumpType.INVALID
        new_trump_type = self.get_trump_type(cards)

        if new_trump_type <= current_trump_type:
            return False, f'{cards} Cannot overwrite current trump: {self.__current_trump_cards}'
        # Allow same player to fortify but not change previously declared trump.
        if player.player_name == self.__trump_declarer and (not (new_trump_type == TrumpType.PAIR and current_trump_type == TrumpType.SINGLE and cards[0].suit == self.__current_trump_cards[0].suit)):
            return False, f'{player.player_name} Cannot overwrite their previous declaration: {self.__current_trump_cards} with {cards}'

        self.__current_trump_cards = cards
        self.__trump_declarer = player.player_name
        if self.__current_rank == Rank.TWO:
            self.__kitty_player_name = self.__trump_declarer
        self.__update_players(lambda unused_game_proto: None)

        return True, ''

    def __hide_kitty(self, player: Player, cards: Sequence[CardProto]) -> Tuple[bool, str]:
        if (len(cards) != 8):
            return False, 'Incorrect number of cards to hide'

        if not player.can_play_cards(cards):
            return False, f'Player does not possess the cards: {cards}'

        for card in cards:
            player.remove_card(card)
            self.__kitty.append(card)

        self.state = GameState.PLAY

        self.__kitty_hidden_update(player.player_name)

        return True, ''

    def __kitty_hidden_update(self, kitty_player_name: str) -> None:
        def action(game: GameProto):
            game.kitty_hidden_update.kitty_player_name = kitty_player_name
        self.__update_players(action)

    def __new_player_update(self, player_name: str) -> None:
        def action(game: GameProto):
            game.new_player_update.player_name = player_name
        self.__update_players(action)

    def __card_dealt_update(self, player_name: str, card: CardProto) -> None:
        def action(game: GameProto):
            game.card_dealt_update.player_name = player_name
            game.card_dealt_update.card.CopyFrom(card)
        self.__update_players(action)

    def __trick_played_update(self, player_name: str, cards: Sequence[CardProto]) -> None:
        def action(game: GameProto):
            game.trick_played_update.player_name = player_name
            game.trick_played_update.hand_played.cards.extend(list(cards))
        self.__update_players(action)

    def __update_players(self, appendUpdate: Callable[[GameProto], None]) -> None:
        game_proto = self.to_game_proto()
        appendUpdate(game_proto)

        with self.__players_lock:
            players = self.__players.values()

        for player in players:
            player.queue_update(game_proto)
