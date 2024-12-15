import { GamePhase } from "../enums";

export class StartResponse {
    activePlayerId: number;
    deckSize: number;
    gameRank: number;
    phase: GamePhase;

    constructor(jsonObj: any) {
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.deckSize = Number(jsonObj['deckSize']);
        this.gameRank = Number(jsonObj['gameRank']);
        this.phase = jsonObj['phase'] as GamePhase;
    }
}