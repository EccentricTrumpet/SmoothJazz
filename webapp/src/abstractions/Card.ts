import { CardState } from "./states";
import { Suit } from "./enums";

export class Card {
    constructor(
        public id: number,
        public suit: Suit,
        public rank: number,

        // UI controls
        public state: CardState = new CardState(),
        public prevState: CardState | undefined = undefined
    ) {}

    public prepareState() {
        this.prevState = this.state;
        this.state = this.state.clone();
    }

    public clone() : Card {
        return new Card(
            this.id,
            this.suit,
            this.rank,
            this.state.clone(),
            this.state,
        )
    }

    public toString = () : string => {
        return `[${this.state.selected ? '*' : ''}Card id: ${this.id} suit: ${this.suit} rank: ${this.rank} state: ${!!this.state} prevState: ${!!this.prevState}]`;
    }
}