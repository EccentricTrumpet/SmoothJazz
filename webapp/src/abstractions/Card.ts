import { Suit } from "./enums";

export class Card {
    constructor( public id: number, public suit: Suit, public rank: number ) {}

    public toString = () => `[ CardInfo id: ${this.id} suit: ${this.suit} rank: ${this.rank} ]`;
    public static fromJson = (jsonObj: {id: string, suit: string, rank: string}) =>
        new Card(Number(jsonObj.id), jsonObj.suit as Suit, Number(jsonObj.rank))
}