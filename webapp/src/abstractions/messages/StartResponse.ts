import { GamePhase } from "../enums";

export class StartResponse {
    activePlayerId: number;
    deckSize: number;
    gameRank: number;
    gamePhase: GamePhase;

    constructor(jsonObj: any) {
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.deckSize = Number(jsonObj['deckSize']);
        this.gameRank = Number(jsonObj['gameRank']);
        this.gamePhase = jsonObj['gamePhase'] as GamePhase;
    }
}