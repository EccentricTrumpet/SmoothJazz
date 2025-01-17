import { CardState } from "./states";

export interface IControl {
    pick: (card: CardState) => void;
    draw: () => void;
    bid: () => void;
    hide: () => void;
    play: () => void;
    next: () => void;
    leave: () => void;
}