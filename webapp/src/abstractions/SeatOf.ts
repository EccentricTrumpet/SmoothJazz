import { Constants } from "../Constants";
import { Seat } from "./enums";

export const seatOf = (playerIndex: number, offset: number, seats: number): Seat => {
    const seatingArrangement = Constants.seatingArrangement[seats];
    return seatingArrangement[(playerIndex + seats - offset) % seats];
}