import { Suit } from "../enums";
import { Card } from "..";

export class PlayResponse {
    playerId: number;
    cards: Card[] = [];
    activePlayerId: number;
    trickWinnerId: number;

    constructor(jsonObj: any) {
        this.playerId = Number(jsonObj['playerId']);
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.trickWinnerId = Number(jsonObj['trickWinnerId']);
        for (const card of jsonObj.cards) {
            this.cards.push(new Card(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}