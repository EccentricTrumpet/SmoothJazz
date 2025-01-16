import { CardUIState } from ".";
import { Card } from "..";
import { Suit } from "../enums";

export class CardState {
    constructor(
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
        this.next.selected = false;
    }

    public toCard = () => new Card(this.id, this.suit, this.rank);
    public toString = () => `[Card id: ${this.id} suit: ${this.suit} rank: ${this.rank}]`;
    public toImg = () => `${this.suit}${this.rank}.png`;
}