import { seatOf } from "../../Constants";
import { PlayerState } from "../states";

export class MatchResponse {
    id: number;
    debug: boolean;
    seats: number;
    southSeat: number;
    players: PlayerState[] = [];

    constructor(jsonText: string) {
        console.log(`raw match response: ${jsonText}`);
        const jsonObj = JSON.parse(jsonText);
        this.id = Number(jsonObj["id"]);
        this.debug = Boolean(jsonObj["debug"]);
        this.seats = Number(jsonObj["seats"]);
        this.southSeat = jsonObj.players.length;
        for (let i = 0; i < this.southSeat; i++) {
            const player = jsonObj.players[i];
            this.players.push(new PlayerState(
                Number(player.pid),
                player.name,
                Number(player.level),
                seatOf(i, this.southSeat, this.seats)
            ));
        }
    }
}