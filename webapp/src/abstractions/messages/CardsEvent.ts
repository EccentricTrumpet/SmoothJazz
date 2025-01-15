import { Card } from "..";

export class CardsEvent {
    constructor(public matchId: number, public playerId: number, public cards: Card[]) {}
}