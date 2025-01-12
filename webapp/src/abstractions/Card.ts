import { Suit } from "./enums";

export class Card {
    constructor(
        public id: number,
        public suit: Suit,
        public rank: number,
    ) {}

    public static fromJson(jsonObj: {id: string, suit: string, rank: string}): Card {
        return new Card(Number(jsonObj.id), jsonObj.suit as Suit, Number(jsonObj.rank))
    }

    public toString = () : string => {
        return `[ CardInfo id: ${this.id} suit: ${this.suit} rank: ${this.rank} ]`;
    }
}