import { Card } from "./Card";

export interface ControllerInterface {
    onSelect: (card: Card) => any;
    onDraw: () => any;
    onBid: () => any;
    onHide: () => any;
    onPlay: () => any;
    onNext: () => any;
    onLeave: () => any;
}