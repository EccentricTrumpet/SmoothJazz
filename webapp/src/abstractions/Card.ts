import { Suit } from "./enums";

export class Card {
    constructor(
        public id: number,
        public suit: Suit,
        public rank: number,
    ) {}

    public toString = () : string => {
        return `[ CardInfo id: ${this.id} suit: ${this.suit} rank: ${this.rank} ]`;
    }
}