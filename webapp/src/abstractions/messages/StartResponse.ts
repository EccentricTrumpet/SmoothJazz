import { GamePhase } from "../enums";

export class StartResponse {
    activePlayerId: number;
    kittyPlayerId: number;
    attackers: number[];
    defenders: number[];
    deckSize: number;
    gameRank: number;
    phase: GamePhase;

    constructor(jsonObj: any) {
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.kittyPlayerId = Number(jsonObj['kittyPlayerId']);
        this.attackers = jsonObj['attackers'].map(Number);
        this.defenders = jsonObj['defenders'].map(Number);
        this.deckSize = Number(jsonObj['deckSize']);
        this.gameRank = Number(jsonObj['gameRank']);
        this.phase = jsonObj['phase'] as GamePhase;
    }
}