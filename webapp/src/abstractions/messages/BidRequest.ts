import { Card } from "..";

export class BidRequest {
    constructor(
        public matchId: number,
        public playerId: number,
        public cards: Card[],
    ) {}
}