import { Position } from "./Position";
import { Suit } from "./Suit";

export class Card {
    constructor(
        public id: number,
        public suit: Suit,
        public rank: number,
        public facedown: boolean = false,
        public position: Position = new Position(0, 0, 0)
    ) {}

    public toString = () : string => {
        return `[Card id: ${this.id} suit: ${this.suit} rank: ${this.rank}]`;
    }
}