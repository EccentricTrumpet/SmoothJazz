import { Card } from "../Card";

// Similar to GameState but this contains visible states
export class BoardState {
    constructor(
        public deck: Card[] = [],
        public kitty: Card[] = [],
        public discard: Card[] = [],
        public points: number = 0,
    ) {}
}