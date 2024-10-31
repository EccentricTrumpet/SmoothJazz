import { Card } from "../Card";
import { Seat } from "../enums";

export class PlayerState {
    constructor(
        public name: string,
        public id: number,
        public index: number,
        public seat: Seat,
        public hand: Card[] = []
    ) {}
}