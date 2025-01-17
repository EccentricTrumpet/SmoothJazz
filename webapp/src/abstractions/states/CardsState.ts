import { Cards } from "./CardState";

// Board sub-state
export class CardsState {
    constructor(public deck: Cards = [], public kitty: Cards = [], public trash: Cards = []) {}

    public update = (val: { deck?: Cards; kitty?: Cards; trash?: Cards; }) =>
        new CardsState(val?.deck ?? this.deck, val?.kitty ?? this.kitty, val?.trash ?? this.trash);
}