import { PlayerState } from "../states";

export class MatchResponse {
    matchId: number;
    debug: boolean;
    numPlayers: number;
    seatOffset: number;
    players: PlayerState[] = [];

    constructor(jsonText: string) {
        console.log(`raw match response: ${jsonText}`);
        var jsonObj = JSON.parse(jsonText);
        this.matchId = Number(jsonObj["id"]);
        this.debug = Boolean(jsonObj["debug"]);
        this.numPlayers = Number(jsonObj["numPlayers"]);
        this.seatOffset = jsonObj.players.length;
        for (let i = 0; i < this.seatOffset; i++) {
            const player = jsonObj.players[i];
            this.players.push(new PlayerState(
                player.id,
                player.name,
                PlayerState.getSeat(i, this.seatOffset, this.numPlayers)
            ));
        }
    }
}