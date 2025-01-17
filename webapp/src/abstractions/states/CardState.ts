import { CardUIState, OptionsState } from ".";
import { Card } from "..";
import { Suit } from "../enums";

export class CardState {
    constructor(
        private options: OptionsState,
        public id: number,
        public suit: Suit = Suit.Unknown,
        public rank: number = 0,

        // UI states
        public next: CardUIState = new CardUIState(),
        public prev: CardUIState | undefined = undefined
    ) {}

    public reset() {
        this.prev = this.next;
        this.next = this.next.clone();
    }

    public update(card: Card) {
        this.reset();
        this.id = card.id;
        this.suit = card.suit;
        this.rank = card.rank;
        this.next.facedown = card.suit === Suit.Unknown;
        this.next.picked = false;
    }

    public card = () => new Card(this.id, this.suit, this.rank);
    public png = () => this.next.facedown ? this.options.cardBack : `${this.suit}${this.rank}.png`;
}

export type Cards = CardState[];