import { GamePhase, Suit } from "../enums";
import { CardInfo } from "./CardInfo";
import { TrickResponse } from "./TrickResponse";

export class EndResponse {
    trick: TrickResponse;
    phase: GamePhase;
    kittyId: number;
    kitty: CardInfo[] = [];
    leadId: number;
    score: number;

    constructor(jsonObj: any) {
        this.trick = new TrickResponse(jsonObj['trick']);
        this.phase = jsonObj['phase'] as GamePhase;
        this.kittyId = Number(jsonObj['kittyId']);
        for (const card of jsonObj.kitty) {
            this.kitty.push(new CardInfo(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
        this.leadId = Number(jsonObj['leadId']);
        this.score = Number(jsonObj['score']);
    }
}