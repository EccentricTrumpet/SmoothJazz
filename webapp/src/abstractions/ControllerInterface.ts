import { Card } from "./Card";

export interface ControllerInterface {
    onSelectCard: (card: Card) => any;
    onDrawCard: () => any;
    onDeclare: (playerId: number) => any;
}