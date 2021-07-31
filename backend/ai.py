import logging
import random
import time
from typing import List
from game_state import (
    Player,
    Game,
    GameState,
    TrumpType,
    getCardNum,
    toCardProto)
from shengji_pb2 import (
    Card as CardProto,
    Game as GameProto)


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
        # Dictionary mapping card to number
        self.__my_cards = dict()
        self.__action_delay_sec = action_delay_sec

    def __try_declare_trump(self, gameProto: GameProto) -> None:
        current_trump_type = self._game.get_trump_type(gameProto.trump_cards.cards)
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
        if success:
            for card_proto in cards_to_play:
                card_num = getCardNum(card_proto)
                self.__my_cards[card_num] -= 1
                if self.__my_cards[card_num] <= 0:
                    del self.__my_cards[card_num]
        return success

    def takeAction(self, gameProto: GameProto) -> None:
        self.__latest_game_proto = gameProto
        if gameProto.HasField('card_dealt_update'):
            logging.info(f'Deal card {gameProto.card_dealt_update.card} to {gameProto.card_dealt_update.player_name}. Updating {self._player_name}. Trump player: {gameProto.trump_player_name}')
            if gameProto.card_dealt_update.player_name == self._player_name:
                self.__try_declare_trump(gameProto)
        if gameProto.state == GameState.AWAIT_TRUMP_DECLARATION and gameProto.trump_player_name == self._player_name:
            time.sleep(self.__action_delay_sec)
            self._game.drawCards(self._player_name)
        if gameProto.state == GameState.HIDE_KITTY and gameProto.trump_player_name == self._player_name:

            time.sleep(self.__action_delay_sec)
            cards_to_play = []
            for card_number in sorted(self.__my_cards.keys(), key=self.__getCardValue):
                count = self.__my_cards[card_number]
                if len(cards_to_play) == 8:
                    break
                if count == 1:
                    cards_to_play.append(toCardProto(card_number))
            self.__try_play_cards(cards_to_play)
        # Keep randomly play a card until succeed.
        if gameProto.state == GameState.PLAY and gameProto.next_turn_player_name == self._player_name:
            cards_on_hand = [p.cards_on_hand for p in gameProto.players if p.player_name == self._player_name][0]
            while True:
                # Assuming no tractor more than 6 cards in real life
                k = random.randint(1, 6)
                cards_to_play = random.sample(list(cards_on_hand.cards), k=k)
                if self.__try_play_cards(cards_to_play):
                    break
