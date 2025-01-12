import { Card } from "..";

export class BidResponse {
    playerId: number;
    trumps: Card[] = [];

    constructor(jsonObj: any) {
        this.playerId = Number(jsonObj['playerId']);
        for (const card of jsonObj.trumps) {
            this.trumps.push(Card.fromJson(card));
        }
    }
}