import { Constants } from "../Constants";
import { Seat } from "./enums";

export const seatOf = (playerIndex: number, seatOffset: number, numPlayers: number): Seat => {
    const seatingArrangement = Constants.seatingArrangement[numPlayers];
    return seatingArrangement[(playerIndex + numPlayers - seatOffset) % numPlayers];
}