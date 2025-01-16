import { Point } from "../bounds";

export class CardUIState {
    constructor(
        public facedown: boolean = true,
        public selected: boolean = false,
        public highlight: boolean = false,
        public rotate: number = 0,
        public origin: Point = new Point(0, 0),
        public delta: Point = new Point(0, 0),
    ) {}

    x = () => this.origin.x + this.delta.x;
    y = () => this.origin.y + this.delta.y;
    clone = () => new CardUIState(
        this.facedown,
        this.selected,
        this.highlight,
        this.rotate,
        this.origin.clone(),
        this.delta.clone()
    );
}