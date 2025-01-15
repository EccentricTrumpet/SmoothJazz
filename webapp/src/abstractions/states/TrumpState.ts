import { CardState } from ".";
import { Suit } from "../enums";

// Board sub-state
export class TrumpState {
    public order = new Map<string, number>();
    public cards: number;
    public rank: number;
    public suit: Suit;

    constructor(
        prev?: TrumpState,
        next?: { numCards?: number; trumpRank?: number; trumpSuit?: Suit; }
    ) {
        this.cards = next?.numCards ?? prev?.cards ?? 0;
        this.rank = next?.trumpRank ?? prev?.rank ?? 0;
        this.suit = next?.trumpSuit ?? prev?.suit ?? Suit.Unknown;
        let nonTrumpSuits: Suit[];
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
            case Suit.Joker:
            case Suit.Unknown:
                nonTrumpSuits = [Suit.Spade, Suit.Heart, Suit.Club, Suit.Diamond];
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
            this.order.set(`${this.suit}${1}`, this.order.size);
            for (let rank = 13; rank > 1; rank--) {
                if (rank !== this.rank) {
                    this.order.set(`${this.suit}${rank}`, this.order.size);
                }
            }
        }

        // Others
        for (const suit of nonTrumpSuits) {
            this.order.set(`${suit}${1}`, this.order.size);
            for (let rank = 13; rank > 1; rank--) {
                if (rank !== this.rank) {
                    this.order.set(`${suit}${rank}`, this.order.size);
                }
            }
        }
    }

    orderOf(card: CardState): number {
        const orderKey = `${card.suit}${card.rank}`;
        if (this.order.has(orderKey)) {
            return this.order.get(orderKey)! * this.cards + card.id;
        }
        return -1
    }
}