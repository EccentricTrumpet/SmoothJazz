import { Card } from "./Card";

export interface IController {
    onPlayCard: (card: Card) => any;
}