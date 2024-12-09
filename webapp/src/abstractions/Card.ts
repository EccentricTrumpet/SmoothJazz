import { CardState } from "./states";
import { Suit } from "./enums";
import { CardInfo } from "./messages";

export class Card {
    constructor(
        public id: number,
        public suit: Suit = Suit.Unknown,
        public rank: number = 0,

        // UI controls
        public state: CardState = new CardState(),
        public prevState: CardState | undefined = undefined
    ) {}

    public resetState() {
        this.prevState = this.state;
        this.state = this.state.clone();
    }

    public updateInfo(info: CardInfo) {
        this.resetState();
        this.id = info.id;
        this.suit = info.suit;
        this.rank = info.rank;
        this.state.facedown = info.suit === Suit.Unknown;
        this.state.selected = false;
    }

    public toInfo(): CardInfo {
        return new CardInfo(this.id, this.suit, this.rank);
    }

    public toString(): string {
        return `[${this.state.selected ? '*' : ''}Card id: ${this.id} suit: ${this.suit} rank: ${this.rank} state: ${!!this.state} prevState: ${!!this.prevState}]`;
    }
}