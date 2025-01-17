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

    reset(next?: { id?: number, suit?: Suit, rank?: number, picked?: boolean, turn?: number }) {
        this.id = next?.id ?? this.id;
        this.suit = next?.suit ?? this.suit;
        this.rank = next?.rank ?? this.rank;
        this.prev = this.next;
        this.next = this.next.clone(next?.picked, next?.turn);
        return this;
    }
    update = (c?: Card, turn?: number) =>
        this.reset({ id: c?.id, suit: c?.suit, rank: c?.rank, picked: false, turn: turn});
    card = () => new Card(this.id, this.suit, this.rank);
    png = () => this.suit === Suit.Unknown ? this.options.back : `${this.suit}${this.rank}.png`;
}

export type Cards = CardState[];