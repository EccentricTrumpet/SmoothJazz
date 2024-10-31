import { CardState } from "./states";
import { Suit } from "./enums";

export class Card {
    constructor(
        public id: number,
        public suit: Suit,
        public rank: number,

        // UI controls
        public state: CardState | undefined = undefined,
        public prevState: CardState | undefined = undefined
    ) {}

    public clone = (state: CardState | undefined = undefined) : Card => {
        return new Card(
            this.id,
            this.suit,
            this.rank,
            state,
            this.state,
        )
    }

    public toString = () : string => {
        return `[Card id: ${this.id} suit: ${this.suit} rank: ${this.rank}]`;
    }
}