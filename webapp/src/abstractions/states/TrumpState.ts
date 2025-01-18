import { CardState } from ".";
import { Suit } from "../enums";

const allRanks = [1, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2];
const nonTrumps: { [suit in Suit]: Suit[] } = {
  [Suit.Joker]: [Suit.Spade, Suit.Heart, Suit.Club, Suit.Diamond],
  [Suit.Unknown]: [Suit.Spade, Suit.Heart, Suit.Club, Suit.Diamond],
  [Suit.Spade]: [Suit.Heart, Suit.Club, Suit.Diamond],
  [Suit.Heart]: [Suit.Spade, Suit.Diamond, Suit.Club],
  [Suit.Club]: [Suit.Heart, Suit.Spade, Suit.Diamond],
  [Suit.Diamond]: [Suit.Spade, Suit.Heart, Suit.Club],
}

// Board sub-state
export class TrumpState {
    private order = new Map<string, number>();

    constructor(private size = 0, public rank = 0, public suit = Suit.Joker) {
        const ranks = allRanks.filter(r => r !== rank);
        let nonTrumpSuits = nonTrumps[suit];

        // Jokers
        this.order.set(`${Suit.Joker}${2}`, this.order.size);
        this.order.set(`${Suit.Joker}${1}`, this.order.size);

        // Trump suit + Trump rank
        if (this.suit !== Suit.Unknown && this.suit !== Suit.Joker)
            this.order.set(`${this.suit}${this.rank}`, this.order.size);

        // Trump rank
        for (const suit of nonTrumpSuits)
            this.order.set(`${suit}${this.rank}`, this.order.size);

        // Trump suit
        if (this.suit !== Suit.Unknown && this.suit !== Suit.Joker)
            ranks.forEach(r => this.order.set(`${this.suit}${r}`, this.order.size));

        // Others
        for (const suit of nonTrumpSuits)
            ranks.forEach(r => this.order.set(`${suit}${r}`, this.order.size));
    }

    orderOf = (c: CardState) => (this.order.get(`${c.suit}${c.rank}`) ?? 0)*this.size + c.id;
    update = (suit?: Suit) => new TrumpState(this.size, this.rank, suit ?? this.suit);
}