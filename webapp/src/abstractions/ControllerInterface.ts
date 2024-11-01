import { Card } from "./Card";

export interface ControllerInterface {
    onSelectCard: (card: Card) => any;
    onDrawCard: (card: Card) => any;
}