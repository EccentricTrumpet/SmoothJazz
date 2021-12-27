import logging
import random
import time
from typing import List
from game_state import (
    Player,
    Game,
    GameState,
    TrumpType)
from shengji_pb2 import (
    Card as CardProto,
    Game as GameProto)

def getCardNum(card: CardProto) -> int:
    return card.suit * 100 + card.rank

def toCardProto(cardNum: int) -> CardProto:
    return CardProto(suit = cardNum // 100, rank = cardNum % 100)

def isJoker(card: CardProto) -> bool:
    return card.suit == CardProto.Suit.SMALL_JOKER or card.suit == CardProto.Suit.BIG_JOKER

class AIBase():
    def __init__(self, game: Game, player: Player) -> None:
        self._player = player
        self._player_name = player.player_name
        self._game = game

    def takeAction(self, gameProto: GameProto) -> None:
        assert False, "takeAction() must be overwritten!"

    def start(self):
        for gameProto in self._player.update_stream():
            self.takeAction(gameProto)

class AaronAI(AIBase):
    def __init__(self, game: Game, player: Player, action_delay_sec=1) -> None:
        super().__init__(game, player)
        self.__action_delay_sec = action_delay_sec

    def __try_declare_trump(self, gameProto: GameProto) -> None:
        current_trump_type = self._game.get_trump_type(gameProto.trump_cards.cards)
        card = gameProto.card_dealt_update.card
        card_as_num = getCardNum(card)
        cards_to_play = []
        if current_trump_type <= TrumpType.NONE and card.rank == self._game.current_rank:
            cards_to_play = [card]
        elif card.rank == self._game.current_rank or card.suit == CardProto.Suit.SMALL_JOKER or card.suit == CardProto.Suit.BIG_JOKER:
            cards_to_play = [card] * 2
        if cards_to_play:
            success, err_str = self._game.play(self._player_name, cards_to_play)
            logging.info(f'Aaron AI {self._player_name} tries to declare trump as {cards_to_play[0]}. Success: {success}; Error: {err_str}')

    def __getCardValue(self, cardNum: int) -> int:
        card_proto = toCardProto(cardNum)
        current_trump_cards = self.__latest_game_proto.trump_cards.cards
        current_trump_suit = CardProto.Suit.SUIT_UNDEFINED
        if current_trump_cards:
            current_trump_suit = current_trump_cards[0].suit
        is_trump_card = isJoker(card_proto) or (card_proto.rank == self.__latest_game_proto.current_rank) or (card_proto.suit == current_trump_suit)
        card_value = 14 if card_proto.rank == 1 else card_proto.rank
        card_value += 10000 if is_trump_card else 0
        card_value += 20 if (card_proto.rank == 13 or card_proto.rank == 10) else 0
        card_value += 10 if (card_proto.rank == 5) else 0
        return card_value

    def __try_play_cards(self, cards_to_play: List[CardProto]) -> bool:
        success, err_str = self._game.play(self._player_name, cards_to_play)
        logging.info(f'Aaron AI {self._player_name} tries to play {cards_to_play}. Success: {success}; Error: {err_str}')
        return success

    def takeAction(self, gameProto: GameProto) -> None:
        self.__latest_game_proto = gameProto
        if gameProto.HasField('card_dealt_update'):
            logging.debug(f'Deal card {gameProto.card_dealt_update.card} to {gameProto.card_dealt_update.player_name}. Updating {self._player_name}. Trump player: {gameProto.trump_player_name}')
            if gameProto.card_dealt_update.player_name == self._player_name:
                self.__try_declare_trump(gameProto)
        if gameProto.state == GameState.AWAIT_TRUMP_DECLARATION and gameProto.trump_player_name == self._player_name:
            time.sleep(self.__action_delay_sec)
            logging.info(f'Aaron AI {self._player_name} draws kitty cards!')
            self._game.draw_cards(self._player_name)
        if gameProto.state == GameState.HIDE_KITTY and gameProto.trump_player_name == self._player_name:

            time.sleep(self.__action_delay_sec)
            cards_on_hand = [p.cards_on_hand for p in gameProto.players if p.player_name == self._player_name][0]
            best_cards_to_play = None
            lowest_value = 9999999999999999
            for _ in range(100):
                cards_to_play = random.sample(list(cards_on_hand.cards), k=8)
                cards_value = sum([self.__getCardValue(getCardNum(c)) for c in cards_to_play])
                if cards_value < lowest_value:
                    best_cards_to_play = cards_to_play
            logging.info(f'Aaron AI {self._player_name} hides kitty with score of {sum([self.__getCardValue(getCardNum(c)) for c in best_cards_to_play])} with {best_cards_to_play}')
            self.__try_play_cards(best_cards_to_play)
        # Keep randomly play cards (up to six), until succeed.
        if gameProto.state == GameState.PLAY and gameProto.next_turn_player_name == self._player_name:
            cards_on_hand = [p.cards_on_hand for p in gameProto.players if p.player_name == self._player_name][0]
            while self._game.state == GameState.PLAY:
                cards_to_play = max([len(p.current_round_trick.cards) for p in gameProto.players])
                cards_to_play = max(cards_to_play, random.randint(1, 4))
                cards_to_play = min(cards_to_play, len(cards_on_hand.cards))
                cards_to_play = random.sample(list(cards_on_hand.cards), k=cards_to_play)
                if self.__try_play_cards(cards_to_play):
                    break
