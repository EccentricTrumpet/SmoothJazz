import { Suit } from "./enums";

const suitChar: { [suit in Suit]: string } = {
    [Suit.Joker]: "",
    [Suit.Unknown]: "",
    [Suit.Spade]: "♠",
    [Suit.Heart]: "♡",
    [Suit.Club]: "♣",
    [Suit.Diamond]: "♢",
}
const rankChar: { [id: number]: string } = {
    1: "A",
    11: "J",
    12: "Q",
    13: "K",
}

export class Card {
    constructor( public id: number, public suit: Suit, public rank: number ) {}

    static fromJson = (jsonObj: {id: string, suit: string, rank: string}) =>
        new Card(Number(jsonObj.id), jsonObj.suit as Suit, Number(jsonObj.rank))

    toString = () => {
        if (this.suit === Suit.Joker)
            return this.rank === 2 ? "Big Joker" : "Small Joker";
        return `${suitChar[this.suit]}${this.rank in rankChar ? rankChar[this.rank] : this.rank}`;
    };
}