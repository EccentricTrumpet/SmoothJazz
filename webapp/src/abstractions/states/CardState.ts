import { CardUIState } from ".";
import { Suit } from "../enums";
import { Card } from "..";

export class CardState {
    constructor(
        public id: number,
        public suit: Suit = Suit.Unknown,
        public rank: number = 0,

        // UI controls
        public state: CardUIState = new CardUIState(),
        public prevState: CardUIState | undefined = undefined
    ) {}

    public resetState() {
        this.prevState = this.state;
        this.state = this.state.clone();
    }

    public updateInfo(info: Card) {
        this.resetState();
        this.id = info.id;
        this.suit = info.suit;
        this.rank = info.rank;
        this.state.facedown = info.suit === Suit.Unknown;
        this.state.selected = false;
    }

    public toInfo(): Card {
        return new Card(this.id, this.suit, this.rank);
    }

    public toString(): string {
        return `[${this.state.selected ? '*' : ''}Card id: ${this.id} suit: ${this.suit} rank: ${this.rank} state: ${!!this.state} prevState: ${!!this.prevState}]`;
    }
}