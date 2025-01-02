import { CardState } from "./states";

export interface ControllerInterface {
    onSelect: (card: CardState) => any;
    onDraw: () => any;
    onBid: () => any;
    onHide: () => any;
    onPlay: () => any;
    onNext: () => any;
    onLeave: () => any;
}