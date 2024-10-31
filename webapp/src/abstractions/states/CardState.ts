import { Position } from "../bounds";

export class CardState {
    constructor(
        public facedown: boolean = false,
        public selected: boolean = false,
        public rotate: number = 0,
        public position: Position = new Position(0, 0),
    ) {}
}