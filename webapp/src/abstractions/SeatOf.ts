import { Constants } from "../Constants";

export const seatOf = (playerIndex: number, offset: number, seats: number) =>
    Constants.seating[seats][(playerIndex + seats - offset) % seats];

