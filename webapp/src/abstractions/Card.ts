import { CardState } from "./states";
import { Suit } from "./enums";

export class Card {
    constructor(
        public id: number,
        public suit: Suit,
        public rank: number,

        // UI controls
        public state: CardState,
        public prevState: CardState
    ) {}

    public clone = () : Card => {
        return new Card(
            this.id,
            this.suit,
            this.rank,
            this.state.clone(),
            this.state.clone(),
        )
    }

    public toString = () : string => {
        return `[${this.state?.selected ? '*' : ''}Card id: ${this.id} suit: ${this.suit} rank: ${this.rank} state: ${!!this.state} prevState: ${!!this.prevState}]`;
    }
}