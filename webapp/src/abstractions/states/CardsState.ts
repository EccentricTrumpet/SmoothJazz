import { CardState } from "./CardState";

// Board sub-state
export class CardsState {
    constructor(
        public deck: CardState[] = [],
        public kitty: CardState[] = [],
        public discard: CardState[] = []
    ) {}

    public update = (next: { deck?: CardState[]; kitty?: CardState[]; discard?: CardState[]; }) =>
        new CardsState(next?.deck ?? this.deck, next?.kitty ?? this.kitty, next?.discard ?? this.discard)
}