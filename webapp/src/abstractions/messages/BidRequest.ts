import { CardInfo } from "./CardInfo";

export class BidRequest {
    constructor(
        public matchId: number,
        public playerId: number,
        public cards: CardInfo[],
    ) {}
}