import { CardInfo } from "./CardInfo";

export class PlayRequest {
    constructor(
        public matchId: number,
        public playerId: number,
        public cards: CardInfo[],
    ) {}
}