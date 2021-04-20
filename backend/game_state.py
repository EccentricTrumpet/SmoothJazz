"""
Game: All state of the game is stored in this class
GameMetadata: Stores states related to the currently playing game
Player class: Contains all player-related states, including cards etc.
Card class: Models a poker card
CardCollection: Organizes cards into useful structures
Hand: A playable hand of cards.
"""

class Game:
    creator_id = None
    players = dict()
    player_ids = []
    metadata = None
    state = None
    next_player_id = None

    # hands on table contains an array of pairs - (id, hand)
    hands_on_table = []
    """
    States:

        Player < 4
    NOT_ENOUGH_PLAYER
        Player == 4
    WAITING_TO_START
        Game started
    WAITING_FOR_PLAYER_<id>
            Game ended, next game pending
        WAITING_TO_START
            Game ended, one of the teams won
        GAME_ENDED
    """

    def __init__(self, player_id):
        self.creator_id = player_id
        self.AddPlayer(player_id)
        self.state = "NOT_ENOUGH_PLAYER"

    def AddPlayer(self, player_id):
        if player_id in self.players.keys():
            return False
        if len(self.players.keys()) == 4:
            return False
        self.players[player_id] = Player()

    # Sets the play order - this should be called exactly once before the first
    # game starts
    def SetPlayerOrder(self, player_ids):
        if self.metadata is not None:
            return False
        self.player_ids = player_ids
        return True

    def StartGame(self, player_id, house_player_id):
        if player_id != creator_id:
            return False
        if self.state == "GAME_ENDED":
            return False

        # init first game
        if self.metadata is None:
            self.metadata = GameMetadata()

        # Reset player states
        for player in self.players.keys():
            self.players[player] = Player(metadata)

        # Deal cards
        self.DealCards()

        # Creator needs to play a hand
        self.state = "WAITING_FOR_PLAYER_" + str(house_player_id)
        self.next_player_id = house_player_id

    def DealCards(self):
        pass

    def Play(self, player_id, cards):
        # Check turn
        if player_id != self.next_player_id:
            return False

        # Check validity
        hand = Hand(cards)

        # Check play cards

        # Update cards on table
        self.hands_on_table.append(tuple(player_id, hand))

        # Compute winner of this round if needed
        if len(self.cards_on_table) == 4:
            self.next_player_id = GetWinnerAndAccumulateScore()
        else:
            self.next_player_id = NextPlayer()

        # Check to see if the game has ended



    def GetWinnerAndAccumulateScore(self):
        # process cards on table in order
        first_hand = hands_on_table[0]
        pass

    def NextPlayer(self):
        pass


class Card:
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

    def IsJoker(self):
        return self.is_small_joker or self.is_big_joker

    def GetIndex(self):
        return self.index;

    def GetSuit(self):
        return self.suit;

    def GetNum(self):
        return self.num;

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
        return index % 13;

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
    trump_suit = None
    trump_card = None

    def __init__(self):
        self.trump_suit = random.choice(["HEARTS", "CLUBS", "DIAMONDS", "SPADES"])
        # 1 maps to 2 in Card
        self.trump_card = 1

class Player:
    card_collection = None
    metadata = None

    def __init__(self, metadata):
        self.metadata = metadata
        self.card_collection = CardCollection()

    def AddCard(self, card):
        self.card_collection.AddCard(card)

    def SwapCards(self, cards_in, cards_out):
        if not self.card_collection.CanRemoveCards(cards_out):
            return False
        self.card_collection.RemoveCards(cards_out)
        self.card_collection.AddCards(cards_in)
        return True

    # Returns true if the given cards can be played
    def CanPlayCards(self, cards, previous_player_hand):
        pass


    def PlayCards(self, cards, previous_player_hand):
        # Returns false if the cards do not form a hand
        hand = Hand(cards)



class CardCollection:
    cards = dict()
    card_count = 0

    # Index cards by suit and num
    by_suit = dict()
    by_num = dict()
    num_small_joker = 0
    num_big_joker = 0

    def __init__(self):
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

    def AddCard(self, card):
        self.cards[card.GetIndex()] += 1
        self.card_count += 1
        self.by_num[card.GetNum()][card.GetSuit()] += 1
        self.by_suit[card.GetSuit()][card.GetNum()] += 1

    def RemoveCard(self, card):
        if self.cards[card.GetIndex()] < 1:
            return False
        self.cards[card.GetIndex()] -= 1
        self.card_count -= 1
        self.by_num[card.GetNum()][card.GetSuit()] -= 1
        self.by_suit[card.GetSuit()][card.GetNum()] -= 1
        return True

    def CanRemoveCards(self, cards):
        current_cards = self.cards
        for card in cards:
            if current_card[card.GetIndex()] < 1:
                return False
            current_cards[card.GetIndex()] -= 1
        return True

    def RemoveCards(self, cards):
        for card in cards:
            if not self.RemoveCard(card):
                return False
        return True

    def GetPlayableHands(self):
        pass

""" A hand represents a valid shengji move, which consists of one of the following
1- A single card of any kind
2- A pair of cards of the same suit
3- Three-of-a-kind
4- Four-of-a-kind (bomb)
5- Straight within the same suit with more than 3 cards
6- Double straight within the same suit with more than 6 cards (straight of pairs, e.g. 334455)
"""
class Hand:
    cards = None
    # Type is SINGLE, PAIR, TOAK, FOAK, STRAIGHT, DOUBLE_STRAIGHT or INVALID
    type = None

    def __init__(self, cards):
        self.cards = cards
        self.type = self.DetectType()

    def VerifyAllCardsEq(self, cards):
        c = cards[0]
        for card in cards:
            if card != c:
                return False
        return True

    def IsValid(self):
        return type != "INVALID"

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

    def __str__(self):
        return self.type + ": " + ",".join([str(c) for c in self.cards])

if __name__ == "__main__":
    print(Hand([Card(1), Card(2), Card(1), Card(2)]))
    print(Hand([Card(1), Card(2), Card(3), Card(4)]))
    print(Hand([Card(1), Card(1), Card(1), Card(1)]))
    print(Hand([Card(1), Card(1), Card(1)]))
    print(Hand([Card(1), Card(1)]))
