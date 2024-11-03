import { PlayerState } from "../states";

export class MatchResponse {
    matchId: number;
    numPlayers: number;
    seatOffset: number;
    players: PlayerState[] = [];

    constructor(jsonText: string) {
        var jsonObj = JSON.parse(jsonText);
        this.matchId = Number(jsonObj["id"]);
        this.numPlayers = Number(jsonObj["numPlayers"]);
        this.seatOffset = jsonObj.players.length;
        for (const player of jsonObj.players) {
            const playerId = Number(player.id);
            this.players.push(new PlayerState(
                playerId,
                player.name,
                PlayerState.getSeat(playerId, this.seatOffset, this.numPlayers)
            ));
        }
    }
}