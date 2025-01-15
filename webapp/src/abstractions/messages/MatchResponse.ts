import { seatOf } from "..";
import { PlayerState } from "../states";

export class MatchResponse {
    id: number;
    debug: boolean;
    seats: number;
    offset: number;
    players: PlayerState[] = [];

    constructor(jsonText: string) {
        console.log(`raw match response: ${jsonText}`);
        const jsonObj = JSON.parse(jsonText);
        this.id = Number(jsonObj["id"]);
        this.debug = Boolean(jsonObj["debug"]);
        this.seats = Number(jsonObj["seats"]);
        this.offset = jsonObj.players.length;
        for (let i = 0; i < this.offset; i++) {
            const player = jsonObj.players[i];
            this.players.push(new PlayerState(undefined, {
                pid: Number(player.pid),
                name: player.name,
                level: Number(player.level),
                seat: seatOf(i, this.offset, this.seats)
            }));
        }
    }
}