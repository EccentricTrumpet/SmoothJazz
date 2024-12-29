import { Card } from "../Card";

// Similar to StatusState but this contains visible states
export class BoardState {
    constructor(
        public deck: Card[] = [],
        public kitty: Card[] = [],
        public discard: Card[] = [],
        public score: number = 0,
    ) {}
}