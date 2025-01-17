import { Cards } from "./CardState";

// Board sub-state
export class CardsState {
    constructor(
        public deck: Cards = [],
        public kitty: Cards = [],
        public discard: Cards = []
    ) {}

    public update = (next: { deck?: Cards; kitty?: Cards; discard?: Cards; }) =>
        new CardsState(
            next?.deck ?? this.deck,
            next?.kitty ?? this.kitty,
            next?.discard ?? this.discard
        );
}