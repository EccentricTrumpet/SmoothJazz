import { Suit } from "../enums";
import { Card } from "..";

export class AlertUpdate {
    title: string = "";
    message: string = "";
    hintCards: Card[] = [];

    constructor(jsonObj: any) {
        this.title = jsonObj.title;
        this.message = jsonObj.message;
        for (const card of jsonObj.hintCards) {
            this.hintCards.push(new Card(
                Number(card.id),
                card.suit as Suit,
                Number(card.rank)
            ));
        }
    }
}