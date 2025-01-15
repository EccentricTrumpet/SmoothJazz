import { CardState } from "./CardState";

// Board sub-state
export class CardsState {
    public deck: CardState[];
    public kitty: CardState[];
    public discard: CardState[];

    constructor(
        prev?: CardsState,
        next?: { deck?: CardState[]; kitty?: CardState[]; discard?: CardState[]; }
    ) {
        this.deck = next?.deck ?? prev?.deck ?? [];
        this.kitty = next?.kitty ?? prev?.kitty ?? [];
        this.discard = next?.discard ?? prev?.discard ?? [];
    }
}