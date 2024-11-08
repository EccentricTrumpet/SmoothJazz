import { Suit } from "../enums";
import { CardInfo } from ".";

export class TrumpResponse {
    playerId: number;
    trumps: CardInfo[] = [];

    constructor(jsonObj: any) {
        this.playerId = Number(jsonObj['playerId']);
        for (const card of jsonObj.trumps) {
            this.trumps.push(new CardInfo(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}