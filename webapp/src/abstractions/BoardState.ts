import { Card } from "./Card";
import { Suit } from "./Suit";

// This will be removed once BE integration is complete
function shuffle<T>(array: T[]): T[] {
    const length = array.length;
    for (let i = length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

export class BoardState {
    constructor(
        initializeDeck: boolean = false,
        public deck: Card[] = [],
        public kitty: Card[] = [],
        public discard: Card[] = [],
        public points: number = 0,
    ) {
        if (initializeDeck) {
            let ids = shuffle(Array.from(Array(108).keys()));
            let cardIndices = shuffle(Array.from(Array(108).keys()));

            for (let i = 0; i < 108; i++) {
                const index = cardIndices[i] % 54;
                let suit = Suit.Joker;
                if (index < 13) {
                suit = Suit.Spade;
                } else if (index < 26) {
                suit = Suit.Heart;
                } else if (index < 39) {
                suit = Suit.Club;
                } else if (index < 52) {
                suit = Suit.Diamond;
                }
                this.deck.push(new Card(ids[i], suit, index % 13 + 1));
            }
        }
    }
}