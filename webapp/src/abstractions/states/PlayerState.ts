import { Constants } from "../../Constants";
import { Card } from "../Card";
import { Seat } from "../enums";

export class PlayerState {
    constructor(
        public id: number,
        public name: string,
        public seat: Seat,
        public hand: Card[] = [],
        public staging: Card[] = []
    ) {}

    public static getSeat(playerId: number, seatOffset: number, numPlayers: number): Seat {
        const seatingArrangement = Constants.seatingArrangement[numPlayers];
        return seatingArrangement[(playerId + numPlayers - seatOffset) % numPlayers];
    }
}