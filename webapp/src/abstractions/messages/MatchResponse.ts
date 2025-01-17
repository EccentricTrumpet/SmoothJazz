import { Seat } from "../enums";
import { PlayerState } from "../states";

const SEATING: {[id: number]: Seat[]} = {
    4: [Seat.South, Seat.East, Seat.North, Seat.West]
}

export const seatOf = (seat: number, southSeat: number, seats: number) =>
    SEATING[seats][(seat + seats - southSeat) % seats];

export class MatchResponse {
    public id = -1;
    public debug = false;
    public seats = -1;
    public players: PlayerState[] = [];

    constructor(jsonText: string) {
        console.log(`raw match response: ${jsonText}`);
        if (jsonText === undefined) return;

        const jsonObj = JSON.parse(jsonText);
        this.id = Number(jsonObj["id"]);
        this.debug = Boolean(jsonObj["debug"]);
        this.seats = Number(jsonObj["seats"]);
        const southSeat = jsonObj.players.length;

        for (let i = 0; i < southSeat; i++) {
            const player = jsonObj.players[i];
            this.players.push(new PlayerState(
                Number(player.pid),
                player.name,
                Number(player.level),
                seatOf(i, southSeat, this.seats)
            ));
        }
    }
}