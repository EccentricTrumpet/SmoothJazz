import { PlayResponse } from "./PlayResponse";

export class TrickResponse {
    score: number;
    activePlayerId: number;
    play: PlayResponse;

    constructor(jsonObj: any) {
        this.score = Number(jsonObj['score']);
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.play = new PlayResponse(jsonObj['play']);
    }
}