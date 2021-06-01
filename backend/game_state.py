import logging
import random
import time
from threading import Semaphore
from collections import deque
from typing import Iterable
from shengji_pb2 import *

class SJPlayer:
    def __init__(self, player_id, notify):
        self._notify = notify
        self._game_queue = deque()
        self._game_queue_sem = Semaphore(0)
        self.player_id = player_id
        self.cards_on_hand = []

    def AddCard(self, card):
        self.cards_on_hand.append(card)

    def ToApiPlayerState(self):
        player_state = PlayerState()
        player_state.player_id = self.player_id
        for card in self.cards_on_hand:
            player_state.cards_on_hand.cards.append(card.ToApiCard())
        return player_state

    def QueueUpdate(self, game: Game):
        if self._notify:
            logging.info(f'updating player: {self.player_id}')
            self._game_queue.append(game)
            self._game_queue_sem.release()

    def CompleteUpdateStream(self):
        self._notify = False
        self._game_queue_sem.release()

    def UpdateStream(self) -> Iterable[Game]:
        while True:
            self._game_queue_sem.acquire()
            logging.info(f'sending update for player: {self.player_id}')
            if self._notify == False: break
            yield self._game_queue.popleft()

"""
Game: All state of the game is stored in this class
GameMetadata: Stores states related to the currently playing game
Player class: Contains all player-related states, including cards etc.
Card class: Models a poker card
CardCollection: Organizes cards into useful structures
Hand: A playable hand of cards.
"""
class SJGame:
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
    def __init__(self, creator_id, game_id, delay):
        self.game_id = game_id
        self.creator_id = creator_id
        self._delay = delay
        self.state = "NOT_ENOUGH_PLAYER"
        self._players = dict()
        self.metadata = None
        self.state = None
        self.next_player_index = 0
        # hands on table contains an array of pairs - (id, hand)
        self.action_count = 0
        self.hands_on_table = []

        # shuffle two decks of cards
        self.deck_cards = [SJCard(x) for x in range(54)] + [SJCard(x) for x in range(54)]
        random.shuffle(self.deck_cards)

    def AddPlayer(self, player_id, notify) -> SJPlayer:
        if player_id in self._players.keys() or len(self._players) == 4:
            return None
        player = SJPlayer(player_id, notify)
        self._players[player_id] = player

        self.UpdatePlayers()

        if len(self._players) == 4:
            self.state = 'NOT_STARTED'

        return player

    def UpdatePlayers(self):
        for player in self._players.values():
            player.QueueUpdate(self.ToApiGame())

    # Returns true if a card was dealt.
    def DealCards(self):
        self.state = "DEALING_CARDS"
        time.sleep(1.0)
        players = list(self._players.values())

        while (len(self.deck_cards) > 8):
            player = players[self.next_player_index]
            player.AddCard(self.deck_cards[0])
            logging.info(f'Dealt card {self.deck_cards[0]} to {player.player_id}')
            self.UpdatePlayers()
            self.next_player_index = (self.next_player_index + 1) % 4
            del self.deck_cards[0]
            time.sleep(self._delay)

        self.state = "CARDS_DEALT"

    def Play(self, player_id, cards):
        # Check turn
        if player_id != self.next_player_id:
            return False

        # Check validity
        hand = Hand(cards)

        # Check play cards
        prev_hand = None
        if len(self.hands_on_table) > 0:
            prev_hand = self.hands_on_table[0][1]

        if not self.players[player_id].CanPlayHand(hand, prev_hand, self.metadata):
            return False

        # play this hand and update cards on table
        self.hands_on_table.append((player_id, hand))
        self.players[player_id].PlayHand(hand)

        # Compute winner of this round if needed
        if len(self.hands_on_table) == 4:
            self.next_player_id = GetWinnerAndAccumulateScore()
        else:
            self.next_player_id = self.NextPlayer()

        # Check to see if the game has ended
        self.action_count += 1
        return True


    def ToApiGame(self):
        game = Game()
        game.game_id = str(self.game_id)
        game.creator_player_id = str(self.creator_id)

        # TODO: Use the real dealer
        game.dealer_player_id = "UNIMPLEMENTED"
        for player in self._players.values():
            game.player_states.append(player.ToApiPlayerState())

        # TODO: Populate kitty

        game.deck_card_count = len(self.deck_cards)
        return game

class SJCard:
    index = None
    suit = None
    """ Modeled the following way to Hand.type detection easier
    0 -> Ace
    1 -> 2
    9  -> 10
    10 -> Jack
    11 -> Queen
    12 -> King
    """
    num = None
    is_small_joker = False
    is_big_joker = False

    def __init__(self, index):
        self.index = index
        self.suit = self.ParseSuit(index)
        self.num = self.ParseNum(index)
        if index == 52:
            self.is_small_joker = True
        if index == 53:
            self.is_big_joker = True

    def __eq__(self, obj):
        return self.index == obj.index

    def __hash__(self):
        return self.index

    def ToApiCard(self):
        card = Card()
        if self.is_small_joker:
            card.suit = Card.Suit.SMALL_JOKER
            return card
        if self.is_big_joker:
            card.suit = Card.Suit.BIG_JOKER
            return card

        if self.GetSuit() == "HEARTS":
            card.suit = Card.Suit.HEARTS
        if self.GetSuit() == "CLUBS":
            card.suit = Card.Suit.CLUBS
        if self.GetSuit() == "DIAMONDS":
            card.suit = Card.Suit.DIAMONDS
        if self.GetSuit() == "SPADES":
            card.suit = Card.Suit.SPADES

        if self.GetNum() == 0:
            card.num = Card.Num.ACE
        if self.GetNum() == 1:
            card.num = Card.Num.TWO
        if self.GetNum() == 2:
            card.num = Card.Num.THREE
        if self.GetNum() == 3:
            card.num = Card.Num.FOUR
        if self.GetNum() == 4:
            card.num = Card.Num.FIVE
        if self.GetNum() == 5:
            card.num = Card.Num.SIX
        if self.GetNum() == 6:
            card.num = Card.Num.SEVEN
        if self.GetNum() == 7:
            card.num = Card.Num.EIGHT
        if self.GetNum() == 8:
            card.num = Card.Num.NINE
        if self.GetNum() == 9:
            card.num = Card.Num.TEN
        if self.GetNum() == 10:
            card.num = Card.Num.JACK
        if self.GetNum() == 11:
            card.num = Card.Num.QUEEN
        if self.GetNum() == 12:
            card.num = Card.Num.KING
        return card


    def IsJoker(self):
        return self.is_small_joker or self.is_big_joker

    def GetIndex(self):
        return self.index

    def GetSuit(self):
        return self.suit

    def GetNum(self):
        return self.num

    def ParseSuit(self, index):
        if int(index / 13) == 0:
            return "HEARTS"
        if int(index / 13) == 1:
            return "CLUBS"
        if int(index / 13) == 2:
            return "DIAMONDS"
        if int(index / 13) == 3:
            return "SPADES"
        return None

    def ParseNum(self, index):
        return index % 13

    def __str__(self):
        if self.is_small_joker:
            return "SMALL_JOKER"
        if self.is_big_joker:
            return "BIG_JOKER"
        card = ""
        if self.num == 10:
            card = "JACK"
        elif self.num == 11:
            card = "QUEEN"
        elif self.num == 12:
            card = "KING"
        elif self.num == 0:
            card = "ACE"
        else:
            card = str(self.num + 1)
        card += "_OF_"
        card += self.suit
        return card

class GameMetadata:
    def __init__(self):
        self.trump_suit = random.choice(["HEARTS", "CLUBS", "DIAMONDS", "SPADES"])
        # 1 maps to 2 in Card
        self.trump_num = 1

    def NextGame(self):
        self.trump_suit = random.choice(["HEARTS", "CLUBS", "DIAMONDS", "SPADES"])


def IsTrumpCard(card, metadata):
    if card.is_small_joker or card.is_big_joker:
        return True
    if metadata.trump_suit == card.suit:
        return True
    if metadata.trump_num == card.num:
        return True
    return False

def GetSuit(card, metadata):
    if card.is_small_joker or card.is_big_joker:
        return metadata.trump_suit
    return card.suit

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

        for suit in ["HEARTS", "CLUBS", "DIAMONDS", "SPADES"]:
            self.by_suit[suit] = dict()
            for num in range(13):
                self.by_suit[suit][num] = 0

        for num in range(13):
            self.by_num[num] = dict()
            for suit in ["HEARTS", "CLUBS", "DIAMONDS", "SPADES"]:
                self.by_num[num][suit] = 0

    def AddCards(self, cards):
        for card in cards:
            self.AddCard(card)

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


    def AddCard(self, card):
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
        string = ""
        for c in self.cards.keys():
            if self.cards[c] > 0:
                string += ", " + str(Card(c)) + "x" + str(self.cards[c])

        return string

""" A hand represents a valid shengji move, which consists of one of the following
1- A single card of any kind
2- A pair of cards of the same suit
3- Three-of-a-kind
4- Four-of-a-kind (bomb)
5- Straight within the same suit with more than 3 cards
6- Double straight within the same suit with more than 6 cards (straight of pairs, e.g. 334455)
"""
class Hand:

    def __init__(self, cards):
        self.cards = cards
        # Type is SINGLE, PAIR, TOAK, FOAK, STRAIGHT, DOUBLE_STRAIGHT or INVALID
        self.type = self.DetectType()

    def VerifyAllCardsEq(self, cards):
        c = cards[0]
        for card in cards:
            if card != c:
                return False
        return True

    # four of a kinds == bomb
    # pair of jokers == bomb
    def IsBomb(self):
        return self.type == "FOAK" or (self.type == "PAIR" and self.cards[0].IsJoker())

    def IsStraight(self, cards):
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

    def IsDoubleStraight(self, cards):
        grouped_cards = dict()
        for card in cards:
            if card.GetIndex() not in grouped_cards.keys():
                grouped_cards[card.GetIndex()] = 0
            grouped_cards[card.GetIndex()] += 1
        count = None

        # equal #s of cards
        for index in grouped_cards.keys():
            if count is None:
                count = grouped_cards[index]
            if count != grouped_cards[index]:
                return False
        return self.IsStraight([Card(c) for c in grouped_cards.keys()])


    def DetectType(self):
        type = "OTHER"
        if len(self.cards) == 1:
            type = "SINGLE"
        elif len(self.cards) == 2 and self.VerifyAllCardsEq(self.cards):
            type = "PAIR"
        elif len(self.cards) == 3 and self.VerifyAllCardsEq(self.cards):
            type = "TOAK"
        elif len(self.cards) == 4 and self.VerifyAllCardsEq(self.cards):
            type = "FOAK"
        elif len(self.cards) >= 3 and self.IsStraight(self.cards):
            type = "STRAIGHT"
        elif len(self.cards) >= 4 and self.IsDoubleStraight(self.cards):
            type = "DOUBLE_STRAIGHT"
        return type

    # Converts to API card representation
    def ToApiCard(self, api_card):
        pass

    # Converts from API card representation
    @classmethod
    def FromApiCard(cls, api_card):
        pass

    def __str__(self):
        return self.type + ": " + ",".join([str(c) for c in self.cards])
