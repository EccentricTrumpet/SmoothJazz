import { CardState } from "./states";

export interface ControllerInterface {
    onSelect: (card: CardState) => void;
    onDraw: () => void;
    onBid: () => void;
    onHide: () => void;
    onPlay: () => void;
    onNext: () => void;
    onLeave: () => void;
}