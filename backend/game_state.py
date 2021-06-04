import logging
import random
import time
from threading import RLock, Semaphore
from collections import deque
from typing import Dict, Iterable, List, Sequence
from shengji_pb2 import (
    Card as CardProto,
    Game as GameProto,
    Player as PlayerProto)


class Card:
    """ Modeled the following way to Hand.type detection easier
    0 -> Ace
    1 -> 2
    9  -> 10
    10 -> Jack
    11 -> Queen
    12 -> King
    """
    def __init__(self, index: int) -> None:
        self.index: int = index
        self.__suit: str = Card.parse_suit(index)
        self.__num: int = Card.parse_num(index)
        self.__is_small_joker: bool = index == 52
        self.__is_big_joker: bool = index == 53

    def __eq__(self, obj: any) -> bool:
        if not isinstance(obj, Card):
            return NotImplemented
        return self.index == obj.index

    def __hash__(self) -> int:
        return self.index

    def to_card_proto(self) -> CardProto:
        card = CardProto()
        if self.__is_small_joker:
            card.suit = CardProto.Suit.SMALL_JOKER
            return card
        if self.__is_big_joker:
            card.suit = CardProto.Suit.BIG_JOKER
            return card

        if self.__suit == 'HEARTS':
            card.suit = CardProto.Suit.HEARTS
        if self.__suit == 'CLUBS':
            card.suit = CardProto.Suit.CLUBS
        if self.__suit == 'DIAMONDS':
            card.suit = CardProto.Suit.DIAMONDS
        if self.__suit == 'SPADES':
            card.suit = CardProto.Suit.SPADES

        if self.__num == 0:
            card.num = CardProto.Num.ACE
        if self.__num == 1:
            card.num = CardProto.Num.TWO
        if self.__num == 2:
            card.num = CardProto.Num.THREE
        if self.__num == 3:
            card.num = CardProto.Num.FOUR
        if self.__num == 4:
            card.num = CardProto.Num.FIVE
        if self.__num == 5:
            card.num = CardProto.Num.SIX
        if self.__num == 6:
            card.num = CardProto.Num.SEVEN
        if self.__num == 7:
            card.num = CardProto.Num.EIGHT
        if self.__num == 8:
            card.num = CardProto.Num.NINE
        if self.__num == 9:
            card.num = CardProto.Num.TEN
        if self.__num == 10:
            card.num = CardProto.Num.JACK
        if self.__num == 11:
            card.num = CardProto.Num.QUEEN
        if self.__num == 12:
            card.num = CardProto.Num.KING
        return card

    @classmethod
    def parse_suit(self, index: int) -> str:
        if int(index / 13) == 0:
            return 'HEARTS'
        if int(index / 13) == 1:
            return 'CLUBS'
        if int(index / 13) == 2:
            return 'DIAMONDS'
        if int(index / 13) == 3:
            return 'SPADES'
        return None

    @classmethod
    def parse_num(self, index: int) -> int:
        return index % 13

    def __str__(self) -> str:
        if self.__is_small_joker:
            return 'SMALL_JOKER'
        if self.__is_big_joker:
            return 'BIG_JOKER'

        if self.__num == 10:
            card = 'JACK'
        elif self.__num == 11:
            card = 'QUEEN'
        elif self.__num == 12:
            card = 'KING'
        elif self.__num == 0:
            card = 'ACE'
        else:
            card = str(self.__num + 1)
        card += '_OF_'
        card += self.__suit
        return card


class Player:
    def __init__(self, player_id: str, notify: bool) -> None:
        self.player_id: str = player_id
        self.__notify: bool = notify
        self.__game_queue: deque[GameProto]  = deque()
        self.__game_queue_sem: Semaphore= Semaphore(0)
        self.__cards_on_hand: list[Card] = []

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

"""
Game: All state of the game is stored in this class
GameMetadata: Stores states related to the currently playing game
Player class: Contains all player-related states, including cards etc.
Card class: Models a poker card
CardCollection: Organizes cards into useful structures
Hand: A playable hand of cards.
"""
class Game:
    """
    States:
        Player < 4
    NOT_ENOUGH_PLAYER
        Player == 4
    NOT_STARTED
        Game started
    WAITING_FOR_PLAYER_<id>
        Game ended, next game pending
    WAITING_TO_START
        Game ended, one of the teams won
    GAME_ENDED
    """

    # API: why do we need creator_id?
    def __init__(self, creator_id: str, game_id: str, delay: float) -> None:
        self.state = 'NOT_ENOUGH_PLAYER'
        self.__game_id: str = game_id
        self.__creator_id: str = creator_id
        self.__delay: float = delay
        self.__players: Dict[str, Player] = dict()
        self.__players_lock: RLock = RLock()
        self.__metadata: GameMetadata = None
        self.__next_player_index: int = 0
        # hands on table contains an array of pairs - (id, hand)
        self.__action_count: int = 0
        self.__hands_on_table: List[tuple[str, Hand]] = []

        # shuffle two decks of cards
        self.__deck_cards: List[Card] = [Card(x) for x in range(54)] + [Card(x) for x in range(54)]
        random.shuffle(self.__deck_cards)

    def add_player(self, player_id: str, notify: bool) -> Player:
        with self.__players_lock:
            if player_id in self.__players.keys() or len(self.__players) == 4:
                return None
            player = Player(player_id, notify)
            self.__players[player_id] = player

            self.__update_players()

            if len(self.__players) == 4:
                self.state = 'NOT_STARTED'

        return player

    def complete_player_stream(self) -> None:
        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            player.complete_update_stream()

    # Returns true if a card was dealt.
    def deal_cards(self) -> None:
        self.state = 'DEALING_CARDS'
        time.sleep(self.__delay)
        with self.__players_lock:
            players = list(self.__players.values())

        while (len(self.__deck_cards) > 8):
            player = players[self.__next_player_index]
            player.add_card(self.__deck_cards[0])
            logging.info(f'Dealt card {self.__deck_cards[0]} to {player.player_id}')
            self.__next_player_index = (self.__next_player_index + 1) % 4
            del self.__deck_cards[0]
            self.__update_players()
            time.sleep(self.__delay)

        self.state = 'CARDS_DEALT'

    def play(self, player_id: str, cards: Sequence[Card]) -> bool:
        # Check turn
        if player_id != self.next_player_id:
            return False

        # Check validity
        hand = Hand(cards)

        # Check play cards
        prev_hand = None
        if len(self.__hands_on_table) > 0:
            prev_hand = self.__hands_on_table[0][1]

        if not self.players[player_id].CanPlayHand(hand, prev_hand, self.__metadata):
            return False

        # play this hand and update cards on table
        self.hands_on_table.append((player_id, hand))
        self.__players[player_id].PlayHand(hand)

        # Compute winner of this round if needed
        if len(self.__hands_on_table) == 4:
            self.next_player_id = GetWinnerAndAccumulateScore()
        else:
            self.next_player_id = self.NextPlayer()

        # Check to see if the game has ended
        self.__action_count += 1
        return True

    def to_game_proto(self) -> GameProto:
        game = GameProto()
        game.game_id = self.__game_id
        game.creator_player_id = self.__creator_id

        # TODO: Use the real dealer
        game.dealer_player_id = 'UNIMPLEMENTED'

        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            game.players.append(player.to_player_proto())

        # TODO: Populate kitty

        game.deck_card_count = len(self.__deck_cards)
        return game

    def __update_players(self) -> None:
        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            player.queue_update(self.to_game_proto())

# This class needs to be refactored to follow coding styles
class GameMetadata:
    def __init__(self):
        self.trump_suit = random.choice(['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES'])
        # 1 maps to 2 in Card
        self.trump_num = 1

    def NextGame(self):
        self.trump_suit = random.choice(['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES'])


# This class needs to be refactored to follow coding styles
def IsTrumpCard(card, metadata):
    if card.is_small_joker or card.is_big_joker:
        return True
    if metadata.trump_suit == card.suit:
        return True
    if metadata.trump_num == card.num:
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
        self.by_num = dict()

        self.small_joker_count = 0
        self.big_joker_count = 0

        for i in range(54):
            self.cards[i] = 0

        for suit in ['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES']:
            self.by_suit[suit] = dict()
            for num in range(13):
                self.by_suit[suit][num] = 0

        for num in range(13):
            self.by_num[num] = dict()
            for suit in ['HEARTS', 'CLUBS', 'DIAMONDS', 'SPADES']:
                self.by_num[num][suit] = 0

    def add_cards(self, cards):
        for card in cards:
            self.add_card(card)

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
