from abstractions import Card, Cards, Suit

# Jokers
# Red (Big)
JR = "J2"
# Black (Small)
JB = "J1"


# Utility to generate a list of cards
def initialize(cards: list[str]) -> Cards:
    card_list = []
    for card in cards:
        card_list.append(Card(len(card_list), Suit(card[0]), int(card[1:])))
    return card_list
