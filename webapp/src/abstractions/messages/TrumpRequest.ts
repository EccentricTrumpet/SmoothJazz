import { CardInfo } from "./CardInfo";

export class TrumpRequest {
    constructor(
        public matchId: number,
        public playerId: number,
        public trumps: CardInfo[],
    ) {}
}