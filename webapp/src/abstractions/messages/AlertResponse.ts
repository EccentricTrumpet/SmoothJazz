import { Suit } from "../enums";
import { CardInfo } from "./CardInfo";

export class AlertResponse {
    title: string = "";
    message: string = "";
    hintCards: CardInfo[] = [];

    constructor(jsonObj: any) {
        this.title = jsonObj['title'];
        this.message = jsonObj['message'];
        for (const card of jsonObj.hintCards) {
            this.hintCards.push(new CardInfo(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}