import { PlayResponse } from "./PlayResponse";

export class TrickResponse {
    points: number;
    activePlayerId: number;
    play: PlayResponse;

    constructor(jsonObj: any) {
        this.points = Number(jsonObj['points']);
        this.activePlayerId = Number(jsonObj['activePlayerId']);
        this.play = new PlayResponse(jsonObj['play']);
    }
}