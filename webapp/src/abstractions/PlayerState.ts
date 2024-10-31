import { Card } from "./Card";
import { SeatPosition } from "./SeatPosition";

export class PlayerState {
    constructor(
        public name: string,
        public id: number,
        public index: number,
        public seatPosition: SeatPosition,
        public hand: Card[] = []
    ) {}
}