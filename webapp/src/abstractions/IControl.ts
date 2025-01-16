import { CardState } from "./states";

export interface IControl {
    onSelect: (card: CardState) => void;
    onDraw: () => void;
    onBid: () => void;
    onHide: () => void;
    onPlay: () => void;
    onNext: () => void;
    onLeave: () => void;
}