import { Card } from "..";

export class PlayRequest {
    constructor(
        public matchId: number,
        public playerId: number,
        public cards: Card[],
    ) {}
}