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
    clone = (picked?: boolean, turn?: number) => new CardUIState(
        picked ?? this.picked, this.focus, turn ?? this.turn, this.origin.clone(), this.delta.clone()
    );
}