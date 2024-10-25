import { Card } from "./Card";

export class BoardState {
    constructor(
        public deck: Card[] = [],
        public kitty: Card[] = [],
        public discard: Card[] = []
    ) {}
}