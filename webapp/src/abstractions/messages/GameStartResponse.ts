import { GamePhase } from "../enums";

export class GameStartResponse {
    activePlayerId: number;
    deckSize: string;
    gamePhase: GamePhase;

    constructor(jsonObj: any) {
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.deckSize = jsonObj['deckSize'];
        this.gamePhase = jsonObj['gamePhase'] as GamePhase;
    }
}