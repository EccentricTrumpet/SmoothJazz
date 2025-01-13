import { CardState } from "./CardState";

// Similar to StatusState but this contains visible states
export class BoardState {
    constructor(
        public deck: CardState[] = [],
        public kitty: CardState[] = [],
        public discard: CardState[] = [],
        public score: number = 0,
    ) {}
}