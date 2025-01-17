import { Vector } from "../bounds";

export class CardUIState {
    constructor(
        public picked = false,
        public focus = false,
        public turn = 0,
        public origin = new Vector(0, 0),
        public delta = new Vector(0, 0),
    ) {}

    position = () => this.origin.add(this.delta).position();
    clone = () => new CardUIState(
        this.picked, this.focus, this.turn, this.origin.clone(), this.delta.clone()
    );
}