import { Constants } from "../../Constants";
import { Card } from "../Card";
import { Seat } from "../enums";

export class PlayerState {
    constructor(
        public id: number,
        public name: string,
        public seat: Seat,
        public hand: Card[] = [],
        public playing: Card[] = []
    ) {}

    public static getSeat(playerIndex: number, seatOffset: number, numPlayers: number): Seat {
        const seatingArrangement = Constants.seatingArrangement[numPlayers];
        return seatingArrangement[(playerIndex + numPlayers - seatOffset) % numPlayers];
    }
}