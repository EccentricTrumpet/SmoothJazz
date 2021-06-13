import logging
import random
import time
from enum import Enum
from threading import RLock, Semaphore
from collections import deque
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    Sequence,
    Tuple,
    Type,
    TypeVar)
from shengji_pb2 import (
    Card as CardProto,
    Game as GameProto,
    Player as PlayerProto)

"""
Game: All state of the game is stored in this class
GameMetadata: Stores states related to the currently playing game
Player class: Contains all player-related states, including cards etc.
Card class: Models a poker card
CardCollection: Organizes cards into useful structures
Hand: A playable hand of cards.
"""

class Suit(Enum):
    SUIT_UNDEFINED = 0
    SPADES = 1
    HEARTS = 2
    CLUBS = 3
    DIAMONDS = 4
    SMALL_JOKER = 5
    BIG_JOKER = 6
    TRUMP = 7

TCard = TypeVar('TCard', bound='Card')
class Card:
    """ Modeled the following way to Hand.type detection easier
    0 -> Undefined
    1 -> Ace
    2 -> 2
    10  -> 10
    11 -> Jack
    12 -> Queen
    13 -> King
    """
    def __init__(self, suit: Suit, rank: int) -> None:
        self.__suit: Suit = suit
        self.__rank: int = rank

    def __eq__(self, obj: any) -> bool:
        if not isinstance(obj, Card):
            return NotImplemented
        return self.__suit == obj.__suit and self.__rank == obj.__rank

    def to_card_proto(self) -> CardProto:
        card = CardProto()

        if self.__suit == Suit.SMALL_JOKER:
            card.suit = CardProto.Suit.SMALL_JOKER
            return card
        if self.__suit == Suit.BIG_JOKER:
            card.suit = CardProto.Suit.BIG_JOKER
            return card
        if self.__suit == Suit.SUIT_UNDEFINED:
            card.suit = CardProto.Suit.SUIT_UNDEFINED
        if self.__suit == Suit.SPADES:
            card.suit = CardProto.Suit.SPADES
        if self.__suit == Suit.HEARTS:
            card.suit = CardProto.Suit.HEARTS
        if self.__suit == Suit.CLUBS:
            card.suit = CardProto.Suit.CLUBS
        if self.__suit == Suit.DIAMONDS:
            card.suit = CardProto.Suit.DIAMONDS

        card.rank = self.__rank

        return card

    @classmethod
    def from_card_proto(cls: Type[TCard], card_proto: CardProto) -> TCard:
        if card_proto.suit == CardProto.Suit.SMALL_JOKER:
            suit = Suit.SMALL_JOKER
        if card_proto.suit == CardProto.Suit.BIG_JOKER:
            suit = Suit.BIG_JOKER
        if card_proto.suit == CardProto.Suit.SUIT_UNDEFINED:
            suit = Suit.SUIT_UNDEFINED
        if card_proto.suit == CardProto.Suit.SPADES:
            suit = Suit.SPADES
        if card_proto.suit == CardProto.Suit.HEARTS:
            suit = Suit.HEARTS
        if card_proto.suit == CardProto.Suit.CLUBS:
            suit = Suit.CLUBS
        if card_proto.suit == CardProto.Suit.DIAMONDS:
            suit = Suit.DIAMONDS

        return Card(suit, card_proto.rank)

    def __str__(self) -> str:
        if self.__suit == Suit.SMALL_JOKER:
            return 'SMALL_JOKER'
        if self.__suit == Suit.BIG_JOKER:
            return 'BIG_JOKER'

        if self.__rank == 11:
            card = 'JACK'
        elif self.__rank == 12:
            card = 'QUEEN'
        elif self.__rank == 13:
            card = 'KING'
        elif self.__rank == 1:
            card = 'ACE'
        else:
            card = str(self.__rank)
        card += '_OF_'
        card += self.__suit.name
        return card


class Player:
    def __init__(self, player_id: str, notify: bool) -> None:
        self.player_id: str = player_id
        self.__notify: bool = notify
        self.__game_queue: deque[GameProto]  = deque()
        self.__game_queue_sem: Semaphore= Semaphore(0)
        self.__cards_on_hand: list[Card] = []

    def has_card(self, card: Card) -> None:
        hasCard = card in self.__cards_on_hand

        if not hasCard:
            logging.info('cards on hand:')
            for card in self.__cards_on_hand:
                logging.info(card)

        return hasCard

    def remove_card(self, card: Card) -> None:
        self.__cards_on_hand.remove(card)

    def add_card(self, card: Card) -> None:
        self.__cards_on_hand.append(card)

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
        player_proto.player_id = self.player_id
        for card in self.__cards_on_hand:
            player_proto.cards_on_hand.cards.append(card.to_card_proto())
        return player_proto


class GameState(Enum):
    # Waiting for players to join the room
    AWAIT_JOIN = 0
    # Waiting to deal/draw
    AWAIT_DEAL = 1
    # Dealing/drawing
    DEAL = 2
    # Dealing Kitty
    DEAL_KITTY = 3
    # Dealing Kitty
    HIDE_KITTY = 4
    # Playing
    PLAY = 5
    # Round ended
    ROUND_END = 6

class Game:
    def __init__(self, creator_id: str, game_id: str, delay: float) -> None:
        self.state = GameState.AWAIT_JOIN
        self.__game_id: str = game_id
        self.__creator_id: str = creator_id
        self.__kitty_id: str = creator_id
        self.__delay: float = delay
        self.__players: Dict[str, Player] = dict()
        self.__players_lock: RLock = RLock()
        self.__metadata: GameMetadata = None
        self.__next_player_id: str = creator_id
        self.__kitty: List[Card] = []
        self.__update_id: int = 0
        self.__update_lock: RLock = RLock()
        # hands on table contains an array of pairs - (id, hand)
        self.__action_count: int = 0
        self.__hands_on_table: List[tuple[str, Hand]] = []

        # shuffle two decks of cards
        self.__deck_cards: List[Card] = []
        for i in range(2):
            self.__deck_cards.append(Card(Suit.BIG_JOKER, 0))
            self.__deck_cards.append(Card(Suit.SMALL_JOKER, 0))
            for s in Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS:
                for r in range(1, 14):
                    self.__deck_cards.append(Card(s, r))

        random.shuffle(self.__deck_cards)

    def add_player(self, player_id: str, notify: bool) -> Player:
        with self.__players_lock:
            if player_id in self.__players.keys() or len(self.__players) == 4:
                return None
            player = Player(player_id, notify)
            self.__players[player_id] = player

            if len(self.__players) == 4:
                self.state = GameState.AWAIT_DEAL

            self.__new_player_update(player_id)

        return player

    def complete_player_stream(self) -> None:
        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            player.complete_update_stream()

    def play(self, player_id: str, cards: Sequence[Card]) -> Tuple[bool, str]:
        # Check turn
        # TODO (https://github.com/EccentricTrumpet/SmoothJazz/issues/49): Handle out of turn play for trump declarations
        if player_id != self.__next_player_id:
            return False, f'Not the turn of player {player_id}'

        if (self.state == GameState.HIDE_KITTY):
            return self.__hide_kitty(self.__players[player_id], cards)

        # TODO: Update players if play is valid

        # Check validity
        hand = Hand(cards)

        # Check play cards
        prev_hand = None
        if len(self.__hands_on_table) > 0:
            prev_hand = self.__hands_on_table[0][1]

        if not self.players[player_id].CanPlayHand(hand, prev_hand, self.__metadata):
            return False, 'Invalid hand'

        # play this hand and update cards on table
        self.hands_on_table.append((player_id, hand))
        self.__players[player_id].PlayHand(hand)

        # Compute winner of this round if needed
        if len(self.__hands_on_table) == 4:
            self.__next_player_id = GetWinnerAndAccumulateScore()
        else:
            self.__next_player_id = self.NextPlayer()

        # Check to see if the game has ended
        self.__action_count += 1
        return True, ''

    def drawCards(self, player_name: str) -> None:
        if self.state == GameState.AWAIT_DEAL and player_name == self.__creator_id:
            self.__deal_hands()
        elif self.state == GameState.DEAL_KITTY and player_name == self.__kitty_id:
            self.__deal_kitty()

    def to_game_proto(self, increment_update_id: bool = True) -> GameProto:
        with self.__update_lock:
            update_id = self.__update_id
            if increment_update_id:
                self.__update_id += 1

        game = GameProto()
        game.update_id = update_id
        game.game_id = self.__game_id
        game.creator_player_id = self.__creator_id

        # TODO: Use the real dealer
        game.dealer_player_id = 'UNIMPLEMENTED'

        # Hack to communicate state
        game.next_turn_player_id = self.state.name

        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            game.players.append(player.to_player_proto())

        for card in self.__kitty:
            game.kitty.cards.append(card.to_card_proto())

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
            logging.info(f'Dealt card {card} to {player.player_id}')
            deal_index = (deal_index + 1) % 4

            if len(self.__deck_cards) == 8:
                self.state = GameState.DEAL_KITTY
            else:
                time.sleep(self.__delay)

            self.__card_dealt_update(player.player_id, card)

    def __deal_kitty(self) -> None:
        while (len(self.__deck_cards) > 0):
            player = self.__players[self.__next_player_id]
            card = self.__deck_cards.pop()
            player.add_card(card)
            logging.info(f'Dealt kitty card {card} to {player.player_id}')

            if len(self.__deck_cards) == 0:
                self.state = GameState.HIDE_KITTY
            else:
                time.sleep(self.__delay)

            self.__card_dealt_update(player.player_id, card)

    def __hide_kitty(self, player: Player, cards: Sequence[Card]) -> Tuple[bool, str]:
        if (len(cards) != 8):
            return False, 'Incorrect number of cards to hide'

        for card in cards:
            if not player.has_card(card):
                return False, f'Player does not possess the card {card}'

        for card in cards:
            player.remove_card(card)
            self.__kitty.append(card)

        self.state = GameState.PLAY

        self.__kitty_hidden_update(player.player_id)

        return True, ''

    def __kitty_hidden_update(self, kitty_player_id: str) -> None:
        def action(game: GameProto):
            game.kitty_hidden_update.kitty_player_id = kitty_player_id
        self.__update_players(action)

    def __new_player_update(self, player_id: str) -> None:
        def action(game: GameProto):
            game.new_player_update.player_id = player_id
        self.__update_players(action)

    def __card_dealt_update(self, player_id: str, card: Card) -> None:
        def action(game: GameProto):
            game.card_dealt_update.player_id = player_id
            game.card_dealt_update.card.CopyFrom(card.to_card_proto())
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
                string += ', ' + str(Card(c)) + 'x' + str(self.cards[c])

        return string

""" A hand represents a valid shengji move, which consists of one of the following
1- A single card of any kind
2- A pair of cards of the same suit
3- Double straight within the same suit with more than 6 cards (straight of pairs, e.g. 334455)
"""
class Hand:
    def __init__(self, cards: Sequence[Card]) -> None:
        self.__cards: Sequence[Card] = cards
        # Type is SINGLE, PAIR, TOAK, FOAK, STRAIGHT, DOUBLE_STRAIGHT or INVALID
        self.type = self.__detect_type()

    def __verify_all_cards_eq(self, cards: Sequence[Card]) -> bool:
        c = cards[0]
        for card in cards:
            if card != c:
                return False
        return True

    def __is_straight(self, cards: Sequence[Card]) -> bool:
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
        return self.__is_straight([Card(c) for c in grouped_cards.keys()])

    def __detect_type(self) -> str:
        if len(self.__cards) == 1:
            return 'SINGLE'
        elif len(self.__cards) == 2 and self.__verify_all_cards_eq(self.__cards):
            return 'PAIR'
        elif len(self.__cards) >= 4 and self.__is_double_straight(self.__cards):
            return 'DOUBLE_STRAIGHT'
        else:
            return 'OTHER'

    def __str__(self) -> str:
        return self.type + ': ' + ','.join([str(c) for c in self.__cards])
