import { CardInfo } from "./CardInfo";

export class KittyRequest {
    constructor(
        public matchId: number,
        public playerId: number,
        public cards: CardInfo[],
    ) {}
}