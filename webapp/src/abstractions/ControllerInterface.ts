import { Card } from "./Card";

export interface ControllerInterface {
    onSelect: (card: Card) => any;
    onDraw: () => any;
    onShow: (playerId: number) => any;
    onHide: (playerId: number) => any;
    onPlay: (playerId: number) => any;
    onNext: (playerId: number) => any;
}