import { Card } from "../Card";
import { Suit } from "../enums";

export class TrumpState {
    public sortOrder = new Map<string, number>();

    constructor(
        public numCards: number,
        public trumpRank: number,
        public trumpSuit = Suit.Unknown
    ) {
        let nonTrumpSuits: Suit[];
        switch(trumpSuit) {
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
            case Suit.Joker:
            case Suit.Unknown:
                nonTrumpSuits = [Suit.Spade, Suit.Heart, Suit.Club, Suit.Diamond];
        }

        // Jokers
        this.sortOrder.set(`${Suit.Joker}${2}`, this.sortOrder.size);
        this.sortOrder.set(`${Suit.Joker}${1}`, this.sortOrder.size);

        // Trump suit + Trump rank
        if (trumpSuit !== Suit.Unknown && trumpSuit !== Suit.Joker) {
            this.sortOrder.set(`${trumpSuit}${trumpRank}`, this.sortOrder.size);
        }

        // Trump rank
        for (const suit of nonTrumpSuits) {
            this.sortOrder.set(`${suit}${trumpRank}`, this.sortOrder.size);
        }

        // Trump suit
        if (trumpSuit !== Suit.Unknown && trumpSuit !== Suit.Joker) {
            this.sortOrder.set(`${trumpSuit}${1}`, this.sortOrder.size);
            for (let rank = 13; rank > 1; rank--) {
                if (rank !== this.trumpRank) {
                    this.sortOrder.set(`${trumpSuit}${rank}`, this.sortOrder.size);
                }
            }
        }

        // Others
        for (const suit of nonTrumpSuits) {
            this.sortOrder.set(`${suit}${1}`, this.sortOrder.size);
            for (let rank = 13; rank > 1; rank--) {
                if (rank !== this.trumpRank) {
                    this.sortOrder.set(`${suit}${rank}`, this.sortOrder.size);
                }
            }
        }
    }

    getSortOrder(card: Card): number {
        const orderKey = `${card.suit}${card.rank}`;
        if (this.sortOrder.has(orderKey)) {
            return this.sortOrder.get(orderKey)! * this.numCards + card.id;
        }
        return -1
    }
}