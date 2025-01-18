import { Card } from "..";

export class ErrorUpdate {
    title: string = "";
    message: string = "";
    cards: Card[] = [];

    constructor(jsonObj: {title: string, message: string, cards: []}) {
        this.title = jsonObj.title;
        this.message = jsonObj.message;
        jsonObj.cards.map(Card.fromJson).forEach(c => this.cards.push(c));
    }
}