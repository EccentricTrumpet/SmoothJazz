import { CardState } from "./CardState";
import { Seat } from "../enums";

export class PlayerState {
    constructor(
        public id: number,
        public name: string,
        public level: number,
        public seat: Seat,
        public hand: CardState[] = [],
        public playing: CardState[] = []
    ) {}
}