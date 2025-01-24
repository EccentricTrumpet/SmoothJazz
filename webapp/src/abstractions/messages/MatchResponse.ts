import { Seat } from "../enums";
import { PlayerState } from "../states";

const SEATING: {[id: number]: Seat[]} = {
    4: [Seat.South, Seat.East, Seat.North, Seat.West]
}

class MatchSettings {
    seats: number;
    debug: boolean;
    logs: boolean;

    constructor(jsonObj?: any) {
        this.seats =  jsonObj && "seats" in jsonObj ? Number(jsonObj["seats"]) : -1;
        this.debug = jsonObj && "debug" in jsonObj ? Boolean(jsonObj["debug"]) : false;
        this.logs = jsonObj && "logs" in jsonObj ? Boolean(jsonObj["logs"]) : false;
    }
}

export const seatOf = (seat: number, southSeat: number, seats: number) =>
    SEATING[seats][(seat + seats - southSeat) % seats];

export class MatchResponse {
    id = -1;
    settings = new MatchSettings();
    players: PlayerState[] = [];

    constructor(jsonText: string) {
        console.log(`raw match response: ${jsonText}`);
        if (jsonText === undefined) return;

        const jsonObj = JSON.parse(jsonText);
        this.id = Number(jsonObj["id"]);
        this.settings = new MatchSettings(jsonObj.settings);
        const southSeat = jsonObj.players.length;

        for (let i = 0; i < southSeat; i++) {
            const player = jsonObj.players[i];
            this.players.push(new PlayerState(
                Number(player.pid),
                player.name,
                Number(player.level),
                seatOf(i, southSeat, this.settings.seats)
            ));
        }
    }
}