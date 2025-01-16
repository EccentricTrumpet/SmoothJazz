import { CardState } from ".";
import { Suit } from "../enums";

// Board sub-state
export class TrumpState {
    public order = new Map<string, number>();

    constructor(public cards = 0, public rank = 0, public suit = Suit.Unknown) {
        const ranks = [1, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2].filter(r => r !== rank);
        let nonTrumpSuits = [Suit.Spade, Suit.Heart, Suit.Club, Suit.Diamond];
        switch(this.suit) {
            case Suit.Spade:
                nonTrumpSuits = [Suit.Heart, Suit.Club, Suit.Diamond];
                break;
            case Suit.Heart:
                nonTrumpSuits = [Suit.Spade, Suit.Diamond, Suit.Club];
                break;
            case Suit.Club:
                nonTrumpSuits = [Suit.Heart, Suit.Spade, Suit.Diamond];
                break;
            case Suit.Diamond:
                nonTrumpSuits = [Suit.Spade, Suit.Heart, Suit.Club];
                break;
        }

        // Jokers
        this.order.set(`${Suit.Joker}${2}`, this.order.size);
        this.order.set(`${Suit.Joker}${1}`, this.order.size);

        // Trump suit + Trump rank
        if (this.suit !== Suit.Unknown && this.suit !== Suit.Joker) {
            this.order.set(`${this.suit}${this.rank}`, this.order.size);
        }

        // Trump rank
        for (const suit of nonTrumpSuits) {
            this.order.set(`${suit}${this.rank}`, this.order.size);
        }

        // Trump suit
        if (this.suit !== Suit.Unknown && this.suit !== Suit.Joker) {
            ranks.forEach(r => this.order.set(`${this.suit}${r}`, this.order.size));
        }

        // Others
        for (const suit of nonTrumpSuits) {
            ranks.forEach(r => this.order.set(`${suit}${r}`, this.order.size));
        }
    }

    orderOf = (card: CardState) => (this.order.get(`${card.suit}${card.rank}`) ?? 0) * this.cards + card.id;
    update = (suit?: Suit) => new TrumpState(this.cards, this.rank, suit ?? this.suit);
}