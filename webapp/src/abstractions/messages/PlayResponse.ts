import { Suit } from "../enums";
import { CardInfo } from ".";

export class PlayResponse {
    playerId: number;
    cards: CardInfo[] = [];
    activePlayerId: number;
    trickWinnerId: number;

    constructor(jsonObj: any) {
        this.playerId = Number(jsonObj['playerId']);
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.trickWinnerId = Number(jsonObj['trickWinnerId']);
        for (const card of jsonObj.cards) {
            this.cards.push(new CardInfo(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}