export class Card {
    suit: string;
    rank: string;
    x: number;

    constructor(suit: string, rank: string) {
        this.suit = suit;
        this.rank = rank;
        this.x = 0;
    }

    setX(x: number) {
        this.x = x;
    }
}