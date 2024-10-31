import { Card } from "./Card";

export interface ControllerInterface {
    onPlayCard: (card: Card) => any;
    onDrawCard: (card: Card) => any;
}