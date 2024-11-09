import { GamePhase } from "../enums";

export class TrickResponse {
    points: number;
    activePlayerId: number;
    phase: GamePhase;

    constructor(jsonObj: any) {
        this.points = Number(jsonObj['points']);
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.phase = jsonObj['phase'] as GamePhase;
    }
}