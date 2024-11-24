from typing import List
from abstractions.enums import Suit
from abstractions.types import Card

# Jokers
BJ = "J2"
SJ = "J1"


# Utility to generate a list of cards
def initialize_cards(cards: List[str]) -> List[Card]:
    card_list = []
    for card in cards:
        card_list.append(Card(len(card_list), Suit(card[0]), int(card[1:])))
    return card_list
