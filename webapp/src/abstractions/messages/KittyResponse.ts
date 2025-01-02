import { GamePhase, Suit } from "../enums";
import { Card } from "..";

export class KittyResponse {
    playerId: number;
    cards: Card[] = [];
    phase: GamePhase;

    constructor(jsonObj: any) {
        this.playerId = Number(jsonObj['playerId']);
        this.phase = jsonObj['phase'] as GamePhase;
        for (const card of jsonObj.cards) {
            this.cards.push(new Card(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}