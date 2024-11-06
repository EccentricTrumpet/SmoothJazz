import { Card } from "../Card";
import { GamePhase, Suit } from "../enums";

export class DrawResponse {
    id: number;
    phase: GamePhase;
    activePlayerId: number;
    cards: Card[] = [];

    constructor(jsonObj: any) {
        this.id = Number(jsonObj['id']);
        this.phase = jsonObj['phase'] as GamePhase;
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        for (const card of jsonObj.cards) {
            this.cards.push(new Card(
                card['id'],
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}