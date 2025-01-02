import { Card } from "..";

export class KittyRequest {
    constructor(
        public matchId: number,
        public playerId: number,
        public cards: Card[],
    ) {}
}