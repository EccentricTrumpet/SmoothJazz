import { GamePhase, Suit } from "../enums";
import { CardInfo } from ".";

export class DrawResponse {
    id: number;
    phase: GamePhase;
    activePlayerId: number;
    cards: CardInfo[] = [];

    constructor(jsonObj: any) {
        this.id = Number(jsonObj['id']);
        this.phase = jsonObj['phase'] as GamePhase;
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        for (const card of jsonObj.cards) {
            this.cards.push(new CardInfo(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}