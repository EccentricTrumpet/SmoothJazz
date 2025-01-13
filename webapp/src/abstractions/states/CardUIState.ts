import { Position } from "../bounds";

export class CardUIState {
    constructor(
        public facedown: boolean = true,
        public selected: boolean = false,
        public highlighted: boolean = false,
        public rotate: number = 0,
        public position: Position = new Position(0, 0),
        public offset: Position = new Position(0, 0),
    ) {}

    x(): number {
        return this.position.x + this.offset.x;
    }

    y(): number {
        return this.position.y + this.offset.y;
    }

    clone(): CardUIState {
        return new CardUIState(
            this.facedown,
            this.selected,
            this.highlighted,
            this.rotate,
            this.position.clone(),
            this.offset.clone()
        )
    }
}