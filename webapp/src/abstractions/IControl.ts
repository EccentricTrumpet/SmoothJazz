import { CardState } from "./states";

export interface IControl {
    select: (card: CardState) => void;
    draw: () => void;
    bid: () => void;
    hide: () => void;
    play: () => void;
    next: () => void;
    leave: () => void;
}