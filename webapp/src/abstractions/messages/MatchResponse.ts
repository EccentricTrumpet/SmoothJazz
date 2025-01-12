import { seatOf } from "..";
import { PlayerState } from "../states";

export class MatchResponse {
    matchId: number;
    debug: boolean;
    numPlayers: number;
    seatOffset: number;
    players: PlayerState[] = [];

    constructor(jsonText: string) {
        console.log(`raw match response: ${jsonText}`);
        const jsonObj = JSON.parse(jsonText);
        this.matchId = Number(jsonObj["id"]);
        this.debug = Boolean(jsonObj["debug"]);
        this.numPlayers = Number(jsonObj["numPlayers"]);
        this.seatOffset = jsonObj.players.length;
        for (let i = 0; i < this.seatOffset; i++) {
            const player = jsonObj.players[i];
            this.players.push(new PlayerState(
                Number(player.id),
                player.name,
                Number(player.level),
                seatOf(i, this.seatOffset, this.numPlayers)
            ));
        }
    }
}