import { CardState } from "./states";

export interface ControlInterface {
    onSelect: (card: CardState) => void;
    onDraw: () => void;
    onBid: () => void;
    onHide: () => void;
    onPlay: () => void;
    onNext: () => void;
    onLeave: () => void;
}