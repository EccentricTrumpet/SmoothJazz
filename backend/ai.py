import logging
import time
from game_state import (
    Player,
    Game,
    get_trump_type,
    TrumpType)
from shengji_pb2 import (
    Card as CardProto,
    Game as GameProto)

def getCardNum(card: CardProto) -> int:
    return card.suit * 100 + card.rank

def toCardProto(cardNum: int) -> CardProto:
    return CardProto(suit = cardNum // 100, rank = cardNum % 100)

class AIBase():
    def __init__(self, game: Game, player: Player) -> None:
        self._player = player
        self._player_name = player.player_name
        self._game = game

    def makePlayDecision(self, gameProto: GameProto) -> None:
        assert False, "makePlayDecision() must be overwritten!"

    def play(self):
        for gameProto in self._player.update_stream():
            self.makePlayDecision(gameProto)

class AaronAI(AIBase):
    def __init__(self, game: Game, player: Player) -> None:
        super().__init__(game, player)
        self.__my_cards = dict()
        self.__card_count = 0

    def __try_declare_trump(self, gameProto: GameProto) -> None:
        current_trump_type = get_trump_type(gameProto.trump_cards.cards, gameProto.current_rank)
        card = gameProto.card_dealt_update.card
        card_as_num = getCardNum(card)
        self.__my_cards[card_as_num] = self.__my_cards.get(card_as_num, 0) + 1
        cards_to_play = []
        if current_trump_type <= TrumpType.NONE and card.rank == CardProto.Rank.TWO:
            cards_to_play = [card]
        elif self.__my_cards.get(card_as_num) == 2 and (card.rank == CardProto.Rank.TWO and current_trump_type <= TrumpType.SINGLE or card.suit == CardProto.Suit.SMALL_JOKER and current_trump_type <= TrumpType.PAIR or card.suit == CardProto.Suit.BIG_JOKER and current_trump_type <= TrumpType.SMALL_JOKER):
            cards_to_play = [card] * 2
        if cards_to_play:
            success, err_str = self._game.play(self._player_name, cards_to_play)
            logging.info(f'Aaron AI {self._player_name} tries to declare trump as {cards_to_play[0].rank}. Success: {success}; Error: {err_str}')

    def makePlayDecision(self, gameProto: GameProto) -> None:
        if gameProto.HasField('card_dealt_update'):
            self.__card_count += 1
            logging.info(f'Card count: {self.__card_count} - {gameProto.card_dealt_update.player_name} - {self._player_name} - {gameProto.trump_player_name}')
            if gameProto.card_dealt_update.player_name == self._player_name:
                self.__try_declare_trump(gameProto)
        if self.__card_count == 100 and gameProto.trump_player_name == self._player_name:
            time.sleep(1)
            self._game.drawCards(self._player_name)
        if self.__card_count == 108 and gameProto.trump_player_name == self._player_name:
            time.sleep(1)
            cards_to_play = []
            for card_number, count in self.__my_cards.items():
                if len(cards_to_play) == 8:
                    break
                if count == 1:
                    cards_to_play.append(toCardProto(card_number))
            success, err_str = self._game.play(self._player_name, cards_to_play)
            logging.info(f'Aaron AI {self._player_name} plays {cards_to_play}. Success: {success}; Error: {err_str}')
