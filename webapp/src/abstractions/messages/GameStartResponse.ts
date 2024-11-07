import { GamePhase } from "../enums";

export class GameStartResponse {
    activePlayerId: number;
    deckSize: number;
    trumpRank: number;
    gamePhase: GamePhase;

    constructor(jsonObj: any) {
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.deckSize = Number(jsonObj['deckSize']);
        this.trumpRank = Number(jsonObj['trumpRank']);
        this.gamePhase = jsonObj['gamePhase'] as GamePhase;
    }
}