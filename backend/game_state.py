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
HIDDEN_CARD_PROTO = CardProto(suit=Suit.SUIT_UNDEFINED, rank=Rank.RANK_UNDEFINED)

KITTY_COUNT = 8
DECK_OF_CARDS = 2
LEVEL_JUMP = DECK_OF_CARDS*20

class TrumpType(IntEnum):
    INVALID = 0
    NONE = 1
    SINGLE = 2
    PAIR = 3
    SMALL_JOKER = 4
    BIG_JOKER = 5


# Functional ranking
class Ranking:
    def __init__(self, trump_rank: int) -> None:
        self.trump_rank: int = trump_rank
        self.trump_suit: Suit = Suit.SUIT_UNDEFINED
        self.__ranking: Dict[str, int] = dict()
        self.resetOrder(self.trump_suit)

    def resetOrder(self, trump_suit: Suit):
        self.trump_suit = trump_suit
        non_trump_suits: List[Suit] = [Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS]
        if trump_suit in non_trump_suits:
            non_trump_suits.remove(trump_suit)
        ranks: List[Rank] = [Rank.ACE]
        for rank in range(Rank.KING, Rank.TWO - 1, -1):
            ranks.append(rank)
        ranking = 0

        # Jokers
        self.__ranking[str(CardProto(suit=Suit.BIG_JOKER, rank=Rank.RANK_UNDEFINED))] = ranking
        ranking += 1
        self.__ranking[str(CardProto(suit=Suit.SMALL_JOKER, rank=Rank.RANK_UNDEFINED))] = ranking
        ranking += 1

        # Trump suit + rank
        if self.trump_suit != Suit.SUIT_UNDEFINED \
            and self.trump_suit != Suit.BIG_JOKER \
            and self.trump_suit != Suit.SMALL_JOKER:
                self.__ranking[str(CardProto(suit=self.trump_suit, rank=self.trump_rank))] = ranking
                ranking += 1

        # Trump rank
        for suit in non_trump_suits:
            self.__ranking[str(CardProto(suit=suit, rank=self.trump_rank))] = ranking
        ranking += 1

        # Trump suit
        if self.trump_suit != Suit.SUIT_UNDEFINED \
            and self.trump_suit != Suit.BIG_JOKER \
            and self.trump_suit != Suit.SMALL_JOKER:
                for rank in ranks:
                    if rank != self.trump_rank:
                        self.__ranking[str(CardProto(suit=self.trump_suit, rank=rank))] = ranking
                        ranking += 1

        # Others
        for suit in non_trump_suits:
            for rank in ranks:
                if rank != self.trump_rank:
                    self.__ranking[str(CardProto(suit=suit, rank=rank))] = ranking
                    ranking += 1

    # For trick resolution. Smaller integer means larger card.
    def get_rank(self, card: CardProto) -> int:
        return self.__ranking[str(card)]

    def is_trump(self, card: CardProto) -> bool:
        return card.suit == Suit.BIG_JOKER \
            or card.suit == Suit.SMALL_JOKER \
            or card.rank == self.trump_rank \
            or (card.suit == self.trump_suit \
                and self.trump_suit != Suit.SUIT_UNDEFINED)


class Tractor:
    def __init__(self, card: CardProto, length: int, cards: Sequence[CardProto]) -> None:
        self.card: CardProto = card
        self.length: int = length
        self.cards: Sequence[CardProto] = cards

    def __str__(self) -> str:
        return f'{self.card}:{self.length}'


class TrickFormat:
    def __init__(self, suit: Suit, length: int, is_trump: bool, tractors: [Tractor] = None, pairs: [CardProto] = None, singles: [CardProto] = None) -> None:
        self.suit = suit
        self.length = length
        self.is_trump = is_trump
        # Stupid Python, see https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument
        self.tractors: List[Tractor] = tractors if tractors else []
        self.pairs: List[CardProto] = pairs if pairs else []
        self.singles: List[CardProto] = singles if singles else []

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

    def is_multi_trick(self) -> bool:
        return len(self.singles) + len(self.pairs) + len(self.tractors) > 1

    def to_card_protos(self) -> Sequence[CardProto]:
        res = []
        for tractor in self.tractors:
            for card in tractor:
                res.extend([card]*2)
        for pair in self.pairs:
            res.extend([pair]*2)
        res.extend(self.singles)
        return res

    def get_smaller_cards(self, other_format: TrickFormat, ranking: Ranking) -> Tuple[bool, TrickFormat]:
        # Leave smallest tractor on the table if there are other players with larger tractor
        for tractor in self.tractors:
            for other_tractor in other_format.tractors:
                if ranking.get_rank(tractor.card) > ranking.get_rank(other_tractor.card) and tractor.length <= other_tractor.length:
                    logging.info(f'Multitrick comparision losing on tractors: {self} vs {other_format}')
                    return False, TrickFormat(self.suit, tractor.length*2, self.is_trump, tractors = [tractor])

        # Leave smallest pairs on the table if there are other players with larger pairs
        self.pairs.sort(key = lambda c: ranking.get_rank(c))
        other_format.pairs.sort(key = lambda c: ranking.get_rank(c))
        if self.pairs and other_format.pairs and ranking.get_rank(self.pairs[-1]) > ranking.get_rank(other_format.pairs[0]):
            logging.info(f'Multitrick comparision losing on pairs: {self} vs {other_format}')
            return False, TrickFormat(self.suit, 2, self.is_trump, pairs = [self.pairs[-1]])

        # Leave smallest singles on the table if there are other players with larger singles
        self.singles.sort(key = lambda c: ranking.get_rank(c))
        other_format.singles.sort(key = lambda c: ranking.get_rank(c))
        if self.singles and other_format.singles and ranking.get_rank(self.singles[-1]) > ranking.get_rank(other_format.singles[0]):
            logging.info(f'Multitrick comparision losing on singles: {self} vs {other_format}')
            return False, TrickFormat(self.suit, 1, self.is_trump, singles = [self.singles[-1]])
        return True, self

    def __str__(self) -> str:
        if self.length == 0:
            return 'Invalid format'
        if self.suit == Suit.SUIT_UNDEFINED:
            return 'Mixed format'

        res_string = f'Suit: {self.suit}'
        res_string += '\nTractor: '
        for tractor in self.tractors:
            res_string += f'{tractor}, '
        res_string += '\nPairs: '
        for pair in self.pairs:
            res_string += f'{pair}, '
        res_string += '\nSingles: '
        for single in self.singles:
            res_string += f'{single}, '
        return res_string

    @classmethod
    def invalid(cls) -> TrickFormat:
        return TrickFormat(Suit.SUIT_UNDEFINED, 0, False)

    @classmethod
    def is_invalid(cls, format: TrickFormat) -> bool:
        return format.length == 0 and format.suit == Suit.SUIT_UNDEFINED


class Trick:
    def __init__(self, ranking: Ranking) -> None:
        self.__ranking: Ranking = ranking
        self.__trick_format: TrickFormat | None = None
        self.__winning_hand: TrickFormat | None = None
        self.winning_player: Player | None = None
        self.plays_made: int = 0

    # Assume cards have been sorted in descending order
    def _create_format(self, suit: Suit, cards: Sequence[CardProto]) -> TrickFormat:
        if len(cards) < 1:
            return TrickFormat.invalid()
        # All valid formats must be of the same suit
        if self.__ranking.is_trump(cards[0]):
            for card in cards[1:]:
                if not self.__ranking.is_trump(card):
                    return TrickFormat.invalid()
        else:
            for card in cards[1:]:
                if card.suit != suit:
                    return TrickFormat.invalid()

        format: TrickFormat = TrickFormat(suit, len(cards), self.__ranking.is_trump(cards[0]))

        # Resolve singles and pairs
        i: int = 0
        while i < len(cards):
            if i < len(cards) - 1 and str(cards[i]) == str(cards[i+1]):
                format.pairs.append(cards[i])
                i += 2
            else:
                format.singles.append(cards[i])
                i += 1

        # Resolve tractors
        i = 0
        pairs_len = len(format.pairs)
        new_pairs = []
        while i < pairs_len:
            j = i
            tractor_cards = [format.pairs[j]]
            while j < pairs_len-1 and self.__ranking.get_rank(format.pairs[j+1]) - self.__ranking.get_rank(format.pairs[j]) == 1:
                tractor_cards.append(format.pairs[j+1])
                j += 1
            if j != i:
                format.tractors.append(Tractor(format.pairs[i], j-i+1, tractor_cards))
                i = j + 1
            else:
                new_pairs.append(format.pairs[i])
                i += 1

        format.pairs = new_pairs
        format.tractors.sort(key = lambda t: (t.length, self.__ranking.get_rank(t.card)))

        return format


    # Assume cards have been sorted in descending order
    def create_format(self, cards: Sequence[CardProto]) -> TrickFormat:
        if len(cards) < 1:
            return TrickFormat.invalid()
        # All valid formats must be of the same suit
        suit: Suit = cards[0].suit
        if self.__ranking.is_trump(cards[0]):
            for card in cards:
                if not self.__ranking.is_trump(card):
                    return TrickFormat.invalid()
        else:
            for card in cards:
                if card.suit != suit:
                    return TrickFormat.invalid()

        return self._create_format(suit, cards)


    def resolve_format(self, player: Player, cards: Sequence[CardProto]) -> tuple[TrickFormat, str]:
        if self.__trick_format is None:
            format = self.create_format(cards)

            if not TrickFormat.is_invalid(format):
                self.__trick_format = format
                return format, ''
            else:
                return format, 'Invalid lead format'

        if len(cards) != self.__trick_format.length:
            return TrickFormat.invalid(), f'Length of cards played does not match lead. Cards played: {cards}; Lead: {self.__trick_format}'

        # Follow suit if possible
        suit_cards_in_hand: List[CardProto] = []
        suit_total_in_hand = 0
        if self.__trick_format.is_trump:
            suit_cards_in_hand = [c for c in player.hand if self.__ranking.is_trump(c)]
            suit_total_in_hand = len(suit_cards_in_hand)
            suit_cards_in_play: List[CardProto] = [c for c in cards if self.__ranking.is_trump(c)]

            if len(suit_cards_in_play) < min(suit_total_in_hand, len(cards)):
                return TrickFormat.invalid(), f'Not all playable cards of the lead suit were played. Suit cards in play: {suit_cards_in_play}, Suit cards in hand: {suit_total_in_hand}'
        else:
            suit_cards_in_hand = [c for c in player.hand if not self.__ranking.is_trump(c) and self.__trick_format.suit == c.suit]
            suit_total_in_hand = len(suit_cards_in_hand)
            suit_cards_in_play: List[CardProto] = [c for c in cards if not self.__ranking.is_trump(c) and self.__trick_format.suit == c.suit]

            if len(suit_cards_in_play) < min(suit_total_in_hand, len(cards)):
                return TrickFormat.invalid(), f'Not all playable cards of the lead suit were played. Suit cards in play: {suit_cards_in_play}, Suit cards in hand: {suit_total_in_hand}'

        if suit_total_in_hand >= self.__trick_format.length:
            # Full follow
            logging.info('Full follow')

            format: TrickFormat = self.create_format(cards)

            if TrickFormat.is_invalid(format) or format.suit == Suit.SUIT_UNDEFINED:
                raise RuntimeError('Invalid format or mixed hand. This should not occur.')

            hand_format: TrickFormat = self._create_format(format.suit, [c for c in player.hand if format.suit == c.suit])
            hand_tractors: List[Tractor] = [t for t in hand_format.tractors]
            trick_tractors: List[Tractor] = [t for t in format.tractors]
            unsatisfied_tractors: List[Tractor] = []

            for tractor in self.__trick_format.tractors:
                # TODO: handle tractor subsets (i.e. length of 3 satisfies length of 2)
                valid_tractors: List[Tractor] = [t for t in hand_tractors if t.length == tractor.length]
                if len(valid_tractors) > 0:
                    played_tractor: Tractor = None
                    hand_tractor: Tractor = None
                    for trick_tractor in trick_tractors:
                        for valid_tractor in valid_tractors:
                            if trick_tractor.length == valid_tractor.length and str(trick_tractor.card) == str(valid_tractor.card):
                                played_tractor = valid_tractor
                                hand_tractor = valid_tractor

                    if played_tractor == None:
                        logging.info('Not all playable tractors of the lead suit were played.')
                        return TrickFormat.invalid(), 'Not all playable tractors of the lead suit were played.'

                    hand_tractors.remove(hand_tractor)
                    trick_tractors.remove(played_tractor)
                else:
                    unsatisfied_tractors.append(tractor)

            pairs_in_played_tractors: int = sum(tt.length for tt in trick_tractors)
            pairs_in_unsatisfied_tractors: int = sum(ut.length for ut in unsatisfied_tractors)
            pairs_in_hand_tractors: int = sum(ht.length for ht in hand_tractors)

            if len(format.pairs) + pairs_in_played_tractors < min(len(self.__trick_format.pairs) + pairs_in_unsatisfied_tractors, len(hand_format.pairs) + pairs_in_hand_tractors):
                logging.info('Not all playable pairs of the lead suit were played.')
                logging.info(f'Number of pairs played: {len(format.pairs)}')
                logging.info(f'Number of pairs in hand: {len(hand_format.pairs)}')
                logging.info(f'Number of pairs in tractors in hand: {pairs_in_hand_tractors}')

                return TrickFormat.invalid(), 'Not all playable pairs of the lead suit were played.'

            if self.__trick_format.verify(format):
                logging.info('Matching format, valid')
                return format, ''
            else:
                logging.info('Mixed format, valid')
                return TrickFormat(Suit.SUIT_UNDEFINED, len(cards), False), ''

        if suit_total_in_hand > 0 and suit_total_in_hand < self.__trick_format.length:
            # Partial follow
            logging.info('Partial follow')
            return TrickFormat(Suit.SUIT_UNDEFINED, len(cards), False), ''

        if suit_total_in_hand == 0:
            for c in cards:
                if not self.__ranking.is_trump(c):
                    logging.info('Cannot follow, mixed format, valid')
                    return TrickFormat(Suit.SUIT_UNDEFINED, len(cards), False), ''

            # All trumps
            format: TrickFormat = self.create_format(cards)

            if not format.is_trump:
                raise RuntimeError('We shoud never resolve the format when non-trumps follow a leading suit')

            if self.__trick_format.verify(format):
                logging.info('Cannot follow, trumped, valid')
                return format, ''
            else:
                logging.info('Cannot follow, mixed trump format, valid')
                return TrickFormat(Suit.SUIT_UNDEFINED, len(cards), False), ''

        logging.info('Unknown format, invalid')
        return TrickFormat.invalid(), 'Unknown format'


    def play_cards(self, player:Player, cards: Sequence[CardProto], other_player_hands: List[Sequence[CardProto]]) -> tuple[bool, str, Sequence[CardProto]]:
        (resolved_format, message) = self.resolve_format(player, cards)

        if TrickFormat.is_invalid(resolved_format):
            return False, message, None

        if resolved_format.suit != Suit.SUIT_UNDEFINED:
            # Leading play
            if self.__winning_hand == None:
                if resolved_format.is_multi_trick():
                    logging.info(f'Leading player proposes s multi trick on {resolved_format.suit}')
                    for player_hand in other_player_hands:
                        # TODO(Aaron): See if we can avoid all branches on is_trump
                        if resolved_format.is_trump:
                            player_hand_format: TrickFormat = self._create_format(
                                    resolved_format.suit, [c for c in player_hand if self.__ranking.is_trump(c)])
                        else:
                            player_hand_format: TrickFormat = self._create_format(
                                    resolved_format.suit, [c for c in player_hand if resolved_format.suit == c.suit and not self.__ranking.is_trump(c)])
                        is_valid_toss, smaller_resolved_format = resolved_format.get_smaller_cards(player_hand_format, self.__ranking)

                        if not is_valid_toss:
                            self.__trick_format = smaller_resolved_format
                            self.__winning_hand = smaller_resolved_format
                            self.winning_player = player
                            self.plays_made = self.plays_made + 1
                            return True, f'Player cards are not the largest, leaving smallest on the table: {smaller_resolved_format.to_card_protos()}', smaller_resolved_format.to_card_protos()
            # Following play
            else:
                # Since the format isn't mixed, assume the format is matched
                def champ_defends(ranking: Ranking, champ_cards: Sequence[CardProto], challenger_cards: Sequence[CardProto]) -> bool:
                    champ_cards.sort(key = lambda c: ranking.get_rank(c))
                    challenger_cards.sort(key = lambda c: ranking.get_rank(c))
                    for (champ, challenger) in zip(champ_cards, challenger_cards):
                        if ranking.get_rank(challenger) >= ranking.get_rank(champ):
                            return True
                    return False

                # TODO: this trick winning logic is too strict according to wiki, though in my experience it's different.
                # TODO(Aaron): I think this will crash when we have tractors of different length, though we need to add unit tests to make sure.
                if champ_defends(self.__ranking, [t.card for t in self.__winning_hand.tractors], [t.card for t in resolved_format.tractors]):
                    logging.info('Challenger lost on tractor')
                    self.plays_made = self.plays_made + 1
                    return True, '', cards

                if champ_defends(self.__ranking, self.__winning_hand.pairs, resolved_format.pairs):
                    logging.info('Challenger lost on pair')
                    self.plays_made = self.plays_made + 1
                    return True, '', cards

                if champ_defends(self.__ranking, self.__winning_hand.singles, resolved_format.singles):
                    logging.info('Challenger lost on single')
                    self.plays_made = self.plays_made + 1
                    return True, '', cards

                logging.info('Challenger won')

            self.__winning_hand = resolved_format
            self.winning_player = player
        self.plays_made = self.plays_made + 1
        return True, '', cards


    def reset_trick(self) -> None:
        self.__trick_format = None
        self.__winning_hand = None
        self.winning_player = None
        self.plays_made = 0


class Player:
    def __init__(self, ranking: Ranking, player_name: str, notify: bool) -> None:
        self.player_name: str = player_name
        # TODO(Aaron): Cards are sorted and displayed in frontend, we can probably get rid of this field.
        self.ranking: Ranking = ranking
        self.latest_rank: Rank = Rank.TWO
        self.__notify: bool = notify
        self.__game_queue: deque[GameProto]  = deque()
        self.__game_queue_sem: Semaphore= Semaphore(0)
        self.current_round_trick: Sequence[CardProto] = []
        # Cards must be kept in sorted order
        self.hand: List[CardProto] = []
        self.score: int = 0

    def has_cards(self, cards: Sequence[CardProto]) -> bool:
        # Sort cards. We cannot use ranking.get_rank() to sort as
        # SPADE_2 and HEART_2 have the same rank and may occur in any
        # order.
        cards.sort(key = lambda c: hash(str(c)))
        self.hand.sort(key = lambda c: hash(str(c)))

        # Iterate both sequences in order
        hand_index = 0
        cards_index = 0

        while cards_index < len(cards):
            while hand_index < len(self.hand) and str(cards[cards_index]) != str(self.hand[hand_index]):
                hand_index += 1
            # A card could not be found in hand
            if hand_index >= len(self.hand):
                logging.info(f'Player {self.player_name} does not have {cards[cards_index]}. Current hand: {self.hand}. Cards: {cards}.')
                return False
            # Matched, continue matching until all of cards exist in hand
            cards_index += 1
            hand_index += 1

        return True

    def remove_card(self, card: CardProto) -> None:
        for hand_card in self.hand:
            if str(card) == str(hand_card):
                self.hand.remove(hand_card)
                return
        logging.info(f'Could not remove card {card} from player {self.player_name}')

    def add_card(self, card: CardProto) -> None:
        self.hand.append(card)
        self.hand.sort(key = lambda c: (self.ranking.get_rank(c), c.Suit))

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
        player_proto.score = self.score
        player_proto.latest_rank = self.latest_rank
        for card in self.current_round_trick:
            player_proto.current_round_trick.cards.append(card)
        for card in self.hand:
            player_proto.cards_on_hand.cards.append(card)
        return player_proto


class Game:
    def __init__(self, creator_name: str, game_id: str, delay: float, num_players: int = 4, show_other_player_hands: bool = False) -> None:
        # public
        self.current_rank: Rank = Rank.TWO
        self.state: GameState = GameState.AWAIT_JOIN

        # protected
        self._next_player_name: str = creator_name
        self._kitty_player_name: str = creator_name
        self._total_score: int = 0

        # private, sorted alphabetically
        self.__creator_name: str = creator_name
        self.__current_trump_cards: Sequence[CardProto] = []
        self.__delay: float = delay
        self.__game_id: str = game_id
        self.__kitty: List[CardProto] = []
        self.__num_players: int = num_players
        self.__play_order: Sequence[str] = []
        self.__players: Dict[str, Player] = dict()
        self.__players_lock: RLock = RLock()
        self.__ranking: Ranking = Ranking(self.current_rank)
        self.__trick: Trick = Trick(self.__ranking)
        self.__trump_declarer: str = ''
        self.__update_id: int = 0
        self.__update_lock: RLock = RLock()
        self.__show_other_player_hands: bool = show_other_player_hands
        self.__init_deck()

    def __init_deck(self) -> None:
        # shuffle two decks of cards
        self.__deck_cards: List[CardProto] = []
        for i in range(DECK_OF_CARDS):
            self.__deck_cards.append(CardProto(suit=Suit.BIG_JOKER,rank=Rank.RANK_UNDEFINED))
            self.__deck_cards.append(CardProto(suit=Suit.SMALL_JOKER,rank=Rank.RANK_UNDEFINED))
            for s in Suit.SPADES, Suit.HEARTS, Suit.CLUBS, Suit.DIAMONDS:
                for r in range(Rank.ACE, Rank.KING + 1):
                    self.__deck_cards.append(CardProto(suit=s,rank=r))

        random.shuffle(self.__deck_cards)

    @property
    def get_game_delay(self) -> float:
        return self.__delay

    @classmethod
    def get_score_from_cards(cls, cards: Sequence[CardProto]) -> int:
        res = 0
        for c in cards:
            if c.rank == Rank.KING or c.rank == Rank.TEN:
                res += 10
            elif c.rank == Rank.FIVE:
                res += 5
        return res

    def get_trump_type(self, cards: Sequence[CardProto]) -> TrumpType:
        if len(cards) == 0:
            return TrumpType.NONE
        if len(cards) == 1 and cards[0].rank == self.current_rank:
            return TrumpType.SINGLE
        if len(cards) == 2:
            if cards[0].suit == Suit.SMALL_JOKER and cards[1].suit == Suit.SMALL_JOKER:
                return TrumpType.SMALL_JOKER
            if cards[0].suit == Suit.BIG_JOKER and cards[1].suit == Suit.BIG_JOKER:
                return TrumpType.BIG_JOKER
            if cards[0].suit == cards[1].suit and cards[0].rank == cards[1].rank == self.current_rank:
                return TrumpType.PAIR
        return TrumpType.INVALID

    def add_player(self, player_name: str, notify: bool) -> Player:
        with self.__players_lock:
            if player_name in self.__players.keys() or len(self.__players) == self.__num_players:
                return None
            player = Player(Ranking(self.current_rank), player_name, notify)
            self.__players[player_name] = player

            if len(self.__players) == self.__num_players:
                self.state = GameState.AWAIT_DEAL

            self.__new_player_update(player_name)
        self.__play_order.append(player_name)

        return player

    def complete_player_stream(self) -> None:
        with self.__players_lock:
            players = self.__players.values()
        for player in players:
            player.complete_update_stream()

    def _get_team_players(self, kitty_team: bool) -> Sequence[Player]:
        res = []
        kitty_player_index = self.__play_order.index(self._kitty_player_name)
        for i, player_name in enumerate(self.__play_order):
            # N.B: This won't work for odd number of players.
            ind_offset = (i - kitty_player_index) % 2
            if kitty_team and ind_offset == 0 or (not kitty_team and ind_offset == 1):
                res.append(self.__players[player_name])
        return res

    def play(self, player_name: str, cards: Sequence[CardProto]) -> Tuple[bool, str]:
        logging.info(f'{player_name} plays {cards} at state: {GameState.Name(self.state)}')
        if player_name != self._next_player_name and self.state != GameState.DEAL and self.state != GameState.AWAIT_TRUMP_DECLARATION:
            return False, f'Not the turn of player {player_name}. Next player: {self._next_player_name}'
        if self.__can_declare_trump():
            return self.__declare_trump(self.__players[player_name], cards)

        if (self.state == GameState.HIDE_KITTY):
            return self.__hide_kitty(self.__players[player_name], cards)

        if (self.state == GameState.PLAY):
            player = self.__players[player_name]
            if not player.has_cards(cards):
                return False, f'Player does not possess the cards: {cards}'

            (success, msg_string, cards) = self.__trick.play_cards(player, cards, [self.__players[p_name].hand for p_name in self.__players if p_name != player_name])

            if not success:
                return success, msg_string

            self._next_player_name = self.__play_order[(self.__play_order.index(player_name) + 1) % self.__num_players]
            for card in cards:
                player.remove_card(card)
            player.current_round_trick = cards

            round_terminated = all([len(p.hand) == 0 for p in self.__players.values()])
            if self.__trick.plays_made == self.__num_players:
                current_round_score = self.get_score_from_cards([c for p in self.__players.values() for c in p.current_round_trick])
                if round_terminated:
                    trick_length = len(list(self.__players.values())[0].current_round_trick)
                    current_round_score += self.get_score_from_cards(self.__kitty) * trick_length
                self.__trick.winning_player.score += current_round_score
                self._total_score = sum([s.score for s in self._get_team_players(kitty_team = False)])
                self._next_player_name = self.__trick.winning_player.player_name

            self.__trick_played_update(player_name, cards)

            if self.__trick.plays_made == self.__num_players:
                self.__trick.reset_trick()
                for p in self.__players.values():
                    p.current_round_trick = []
                if round_terminated:
                    logging.info('Current round finished!')
                    non_kitty_team_player_names = ', '.join([p.player_name for p in self._get_team_players(kitty_team = False)])
                    round_res = 'wins' if self._total_score >= LEVEL_JUMP*2 else 'loses'
                    round_end_message = f'Team {non_kitty_team_player_names} {round_res} with a total score of {self._total_score}.'
                    self._reset_round()
                    self.__round_end_update(round_end_message)

            logging.info('successful play')
            return True, msg_string
        return False, f'Unsupported game state: {self.state}'

    def _reset_round(self):
        self.state = GameState.AWAIT_DEAL
        self.__current_trump_cards = []
        self.__trump_declarer = ""
        self.__kitty = []
        self.__init_deck()
        kitty_player_index = self.__play_order.index(self._kitty_player_name)
        if self._total_score < LEVEL_JUMP*2:
            new_kitty_player_index = (kitty_player_index + 2) % self.__num_players
            kitty_team_players = self._get_team_players(kitty_team=True)
            rank_jump = 3 if self._total_score == 0 else (2 if self._total_score < LEVEL_JUMP else 1)
            for p in kitty_team_players:
                p.latest_rank += rank_jump
        else:
            new_kitty_player_index = (kitty_player_index + 1) % self.__num_players
            rank_jump = (self._total_score - LEVEL_JUMP*2) // LEVEL_JUMP
            non_kitty_team_players = self._get_team_players(kitty_team=False)
            for p in non_kitty_team_players:
                p.latest_rank += rank_jump
        self._kitty_player_name = self.__play_order[new_kitty_player_index]
        self.current_rank = self.__players[self._kitty_player_name].latest_rank
        self.__ranking = Ranking(self.current_rank)
        self.__trick = Trick(self.__ranking)
        self._total_score = 0
        for player in self.__players.values():
            player.score = 0
            player.hand = []
            player.current_round_trick = []
            player.ranking = Ranking(self.current_rank)

    def draw_cards(self, player_name: str) -> None:
        if self.state == GameState.AWAIT_DEAL and player_name == self.__creator_name:
            self.__deal_hands()
        elif self.state == GameState.AWAIT_TRUMP_DECLARATION and player_name == self._kitty_player_name:
            self.state = GameState.DEAL_KITTY
            self.__deal_kitty()
            self._next_player_name = self._kitty_player_name

    def to_game_proto(self, increment_update_id: bool = True) -> GameProto:
        with self.__update_lock:
            update_id = self.__update_id
            if increment_update_id:
                self.__update_id += 1

        game = GameProto()
        game.update_id = update_id
        game.game_id = self.__game_id
        game.creator_player_name = self.__creator_name

        game.current_rank = self.current_rank
        game.trump_player_name = self.__trump_declarer
        game.next_turn_player_name = self._next_player_name
        game.trump_cards.cards.extend(self.__current_trump_cards)

        game.kitty_player_name = self._kitty_player_name
        game.total_score = self._total_score
        game.state = self.state

        with self.__players_lock:
            players = self.__players.values()
        game.players.extend([p.to_player_proto() for p in players])

        return game

    def __deal_hands(self) -> None:
        self.state = GameState.DEAL
        with self.__players_lock:
            players = list(self.__players.values())

        deal_index = 0

        while (len(self.__deck_cards) > KITTY_COUNT):
            player = players[deal_index]
            card = self.__deck_cards.pop()
            player.add_card(card)
            logging.info(f'Dealt card {card} to {player.player_name}')
            deal_index = (deal_index + 1) % self.__num_players

            if len(self.__deck_cards) == KITTY_COUNT:
                self.state = GameState.AWAIT_TRUMP_DECLARATION

            time.sleep(self.__delay)
            self.__card_dealt_update(player.player_name, card)

    def __deal_kitty(self) -> None:
        while (len(self.__deck_cards) > 0):
            player = self.__players[self._kitty_player_name]
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
        logging.info(f'{player.player_name} declares trump as: {cards}')

        if not player.has_cards(cards):
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
        if self.current_rank == Rank.TWO:
            self._kitty_player_name = self.__trump_declarer
        self.__ranking.resetOrder(cards[0].suit)
        self.__update_players(lambda unused_game_proto, unused_update_player_name: None)

        return True, ''

    def __hide_kitty(self, player: Player, cards: Sequence[CardProto]) -> Tuple[bool, str]:
        if (len(cards) != KITTY_COUNT):
            return False, f'Incorrect number of cards to hide. Expecting {KITTY_COUNT} cards'

        if not player.has_cards(cards):
            return False, f'Player does not possess the cards: {cards}'

        for card in cards:
            player.remove_card(card)
            self.__kitty.append(card)

        self.state = GameState.PLAY

        self.__kitty_hidden_update(player.player_name)

        return True, ''

    def __kitty_hidden_update(self, kitty_player_name: str) -> None:
        def action(game: GameProto, update_player_name: str):
            game.kitty_hidden_update.kitty_player_name = kitty_player_name
            if update_player_name == kitty_player_name or self.__show_other_player_hands:
                game.kitty.cards.extend(self.__kitty)
            else:
                game.kitty.cards.extend([HIDDEN_CARD_PROTO] * len(self.__kitty))
        self.__update_players(action)

    def __new_player_update(self, player_name: str) -> None:
        def action(game: GameProto, unused_update_player_name: str):
            game.new_player_update.player_name = player_name
        self.__update_players(action)

    def __card_dealt_update(self, player_name: str, card: CardProto) -> None:
        def action(game: GameProto, update_player_name: str):
            game.card_dealt_update.player_name = player_name
            card_to_update = card if update_player_name == player_name or self.__show_other_player_hands else HIDDEN_CARD_PROTO
            game.card_dealt_update.card.CopyFrom(card_to_update)
        self.__update_players(action)

    def __trick_played_update(self, player_name: str, cards: Sequence[CardProto]) -> None:
        def action(game: GameProto, unused_update_player_name: str):
            game.trick_played_update.player_name = player_name
            game.trick_played_update.hand_played.cards.extend(list(cards))
        self.__update_players(action)

    def __round_end_update(self, message: str) -> None:
        def action(game: GameProto, unused_update_player_name: str):
            game.round_end_update.round_end_message = message
        self.__update_players(action)

    def __update_players(self, appendUpdate: Callable[[GameProto, str], None]) -> None:
        with self.__players_lock:
            players = self.__players

        original_game_proto = self.to_game_proto()
        import copy
        for p_name, player in players.items():
            # This is not efficient, but who cares about performance...
            game_proto = copy.deepcopy(original_game_proto)
            appendUpdate(game_proto, p_name)
            logging.debug(f'Updating {p_name} with proto {game_proto}')
            player.queue_update(game_proto)
