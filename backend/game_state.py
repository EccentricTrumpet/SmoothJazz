import logging
import random
import time
from enum import Enum, IntEnum
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
    Hand as HandProto,
    Game as GameProto,
    Player as PlayerProto)

# Type aliases
Suit = CardProto.Suit
Rank = CardProto.Rank

# Utility functions
def is_joker(card: CardProto) -> bool:
    return card.suit == Suit.SMALL_JOKER or card.suit == Suit.BIG_JOKER

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

"""
Game: All state of the game is stored in this class
GameMetadata: Stores states related to the currently playing game
Player class: Contains all player-related states, including cards etc.
CardCollection: Organizes cards into useful structures
Hand: A playable hand of cards.
"""

class Player:
    def __init__(self, player_name: str, notify: bool) -> None:
        self.player_name: str = player_name
        self.__notify: bool = notify
        self.__game_queue: deque[GameProto]  = deque()
        self.__game_queue_sem: Semaphore= Semaphore(0)
        self.cards_on_hand: Dict[CardProto, int] = dict()

    # def has_card(self, card: CardProto) -> bool:
    #     return card in self.cards_on_hand

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
            game_state = self.__game_queue.popleft()
            yield game_state

    def to_player_proto(self) -> PlayerProto:
        player_proto = PlayerProto()
        player_proto.player_name = self.player_name
        for card,count in self.cards_on_hand.items():
            for _ in range(count):
                player_proto.cards_on_hand.cards.append(toCardProto(card))
        return player_proto


class GameState(Enum):
    # Waiting for players to join the game
    AWAIT_JOIN = 0
    # Waiting to deal/draw
    AWAIT_DEAL = 1
    # Dealing/drawing
    DEAL = 2
    # Finished dealing but before dealer clicks to see the kitty
    AWAIT_TRUMP_DECLARATION = 3
    # Dealing Kitty
    DEAL_KITTY = 4
    # Hiding Kitty
    HIDE_KITTY = 5
    # Playing
    PLAY = 6
    # Round ended
    ROUND_END = 7

class Game:
    def __init__(self, creator_name: str, game_id: str, delay: float) -> None:
        self.state = GameState.AWAIT_JOIN
        self.__game_id: str = game_id
        self.__creator_name: str = creator_name
        self.__kitty_player_name: str = creator_name
        self.__delay: float = delay
        self.__players: Dict[str, Player] = dict()
        self.__players_lock: RLock = RLock()
        self.__metadata: GameMetadata = None
        self.__next_player_name: str = creator_name
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
        logging.info(f'Game state: {self.state}')
        if player_name != self.__next_player_name and self.state != GameState.DEAL and self.state != GameState.AWAIT_TRUMP_DECLARATION:
            return False, f'Not the turn of player {player_name}'
        if self.state == GameState.DEAL or self.state == GameState.AWAIT_TRUMP_DECLARATION:
            return self.__declare_trump(self.__players[player_name], cards)

        if (self.state == GameState.HIDE_KITTY):
            return self.__hide_kitty(self.__players[player_name], cards)

        if (self.state == GameState.PLAY):

            if not self.__players[player_name].can_play_cards(cards):
                return False, f'Player does not possess the cards: {cards}'
            self.__hands_on_table.append(Hand(cards))
            self.__next_player_id = self.__play_order[(self.__play_order.index(player_name) + 1) % 4]
            if len(self.__hands_on_table) == 4:
                self.__next_player_id = random.choice(self.__players.keys())
                self.__hands_on_table = []
            return True, ""

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
            self.__next_player_name = GetWinnerAndAccumulateScore()
        else:
            self.__next_player_name = self.NextPlayer()

        # Check to see if the game has ended
        self.__action_count += 1
        return True, ''

    def drawCards(self, player_name: str) -> None:
        if self.state == GameState.AWAIT_DEAL and player_name == self.__creator_name:
            self.__deal_hands()
        elif self.state == GameState.AWAIT_TRUMP_DECLARATION and player_name == self.__kitty_player_name:
            self.state = GameState.DEAL_KITTY
            self.__deal_kitty()
            self.__next_player_name = self.__kitty_player_name

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
        for card in self.__current_trump_cards:
            card_proto = game.trump_cards.cards.add()
            card_proto.CopyFrom(card)

        game.kitty_player_name = self.__kitty_player_name

        # Hack to communicate state
        game.next_turn_player_name = self.state.name

        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            game.players.append(player.to_player_proto())

        for card in self.__kitty:
            game.kitty.cards.append(card)

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

    def __update_players(self, appendUpdate: Callable[[GameProto], None]) -> None:
        game_proto = self.to_game_proto()
        appendUpdate(game_proto)

        with self.__players_lock:
            players = self.__players.values()

        for player in players:
            player.queue_update(game_proto)


# This class needs to be refactored to follow coding styles
class GameMetadata:
    def __init__(self):
        self.trump_suit = random.choice(['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES'])
        self.trump_rank = 2

    def NextGame(self):
        self.trump_suit = random.choice(['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES'])


# This class needs to be refactored to follow coding styles
def IsTrumpCard(card, metadata):
    if card.is_small_joker or card.is_big_joker:
        return True
    if metadata.trump_suit == card.suit:
        return True
    if metadata.trump_rank == card.rank:
        return True
    return False


# This class needs to be refactored to follow coding styles
def GetSuit(card, metadata):
    if card.is_small_joker or card.is_big_joker:
        return metadata.trump_suit
    return card.suit


# This class needs to be refactored to follow coding styles
class CardCollection:
    def __init__(self):
        self.cards = dict()
        self.card_count = 0

        # Index cards by suit and num
        self.by_suit = dict()
        self.by_rank = dict()

        self.small_joker_count = 0
        self.big_joker_count = 0

        for i in range(54):
            self.cards[i] = 0

        for suit in ['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES']:
            self.by_suit[suit] = dict()
            for rank in range(1, 14):
                self.by_suit[suit][rank] = 0

        for rank in range(1, 14):
            self.by_rank[rank] = dict()
            for suit in ['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES']:
                self.by_rank[rank][suit] = 0

    def add_cards(self, cards):
        for card in cards:
            self.add_card(card)

    # What does this do?
    def SuitCount(self, suit):
        count = 0
        # Linear scan at suit
        for num in self.by_suit[suit]:
            count += self.by_suit[num]
        return count

    def HasTrump(metadata):
        if self.small_joker_count > 0 or self.big_joker_count > 0:
            return True
        return self.HasSuit(metadata.trump_suit)

    def HasMultipleCards(self, count=2):
        for c in self.cards.keys():
            if self.cards[c] >= count:
                return True
        return False

    def HasSuit(self, suit, metadata, count=1):
        # Linear scan at suit
        for c in self.by_suit[suit].keys():
            if self.by_suit[suit] >= count:
                return True

        # Also need to scan joker and off-suit trumps
        if suit == metadata.trump_suit:
            if self.small_joker_count >= count:
                return  True
            if self.big_joker_count >= count:
                return  True
        return False


    def add_card(self, card):
        self.cards[card.GetIndex()] += 1
        self.card_count += 1
        if card.is_small_joker:
            self.small_joker_count += 1
            return
        if card.is_big_joker:
            self.big_joker_count += 1
            return
        self.by_num[card.GetNum()][card.GetSuit()] += 1
        self.by_num[card.GetNum()][card.GetSuit()] += 1
        self.by_suit[card.GetSuit()][card.GetNum()] += 1

    def RemoveCard(self, card):
        if self.cards[card.GetIndex()] < 1:
            return False
        self.cards[card.GetIndex()] -= 1
        self.card_count -= 1
        if card.is_small_joker:
            self.small_joker_count -= 1
            return True
        if card.is_big_joker:
            self.big_joker_count -= 1
            return True
        self.by_num[card.GetNum()][card.GetSuit()] -= 1
        self.by_suit[card.GetSuit()][card.GetNum()] -= 1
        return True

    def CanRemoveCards(self, cards):
        current_cards = self.cards
        for card in cards:
            if current_cards[card.GetIndex()] < 1:
                return False
            current_cards[card.GetIndex()] -= 1
        return True

    def RemoveCards(self, cards):
        for card in cards:
            if not self.RemoveCard(card):
                return False
        return True

    def __str__(self):
        string = ''
        for c in self.cards.keys():
            if self.cards[c] > 0:
                string += ', ' + str(CardProto(c)) + 'x' + str(self.cards[c])

        return string

""" A hand represents a valid shengji move, which consists of one of the following
1- A single card of any kind
2- A pair of cards of the same suit
3- Double straight within the same suit with more than 6 cards (straight of pairs, e.g. 334455)
"""
class Hand:
    def __init__(self, cards: Sequence[CardProto]) -> None:
        self.__cards: Sequence[CardProto] = cards
        # Type is SINGLE, PAIR, TOAK, FOAK, STRAIGHT, DOUBLE_STRAIGHT or INVALID
        self.type = self.__detect_type()

    def __verify_all_cards_eq(self, cards: Sequence[CardProto]) -> bool:
        c = cards[0]
        for card in cards:
            if card != c:
                return False
        return True

    def __is_straight(self, cards: Sequence[CardProto]) -> bool:
        if len(cards) < 3:
            return False
        min_card = cards[0].GetNum()
        max_card = cards[0].GetNum()
        suit = cards[0].GetSuit()
        seen_nums = []

        for card in cards:
            if card.GetSuit() != suit:
                return False
            if card.GetNum() in seen_nums:
                return False
            seen_nums.append(card.GetNum())
            min_card = min(min_card, card.GetNum())
            max_card = max(max_card, card.GetNum())
        return (max_card - min_card) == len(cards) - 1

    def __is_double_straight(self, cards) -> bool:
        grouped_cards = dict()
        for card in cards:
            if card.index not in grouped_cards.keys():
                grouped_cards[card.index] = 0
            grouped_cards[card.index] += 1
        count = None

        # equal #s of cards
        for index in grouped_cards.keys():
            if count is None:
                count = grouped_cards[index]
            if count != grouped_cards[index]:
                return False
        return self.__is_straight([CardProto(c) for c in grouped_cards.keys()])

    def __detect_type(self) -> str:
        if len(self.__cards) == 1:
            return 'SINGLE'
        elif len(self.__cards) == 2 and self.__verify_all_cards_eq(self.__cards):
            return 'PAIR'
        # self.__is_double_straight current crashes
        # elif len(self.__cards) >= 4 and self.__is_double_straight(self.__cards):
        #     return 'DOUBLE_STRAIGHT'
        else:
            return 'OTHER'

    def __str__(self) -> str:
        return self.type + ': ' + ','.join([str(c) for c in self.__cards])
