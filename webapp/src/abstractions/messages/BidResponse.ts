import { Suit } from "../enums";
import { Card } from "..";

export class BidResponse {
    playerId: number;
    trumps: Card[] = [];
    kittyPlayerId: number;
    attackers: number[];
    defenders: number[];

    constructor(jsonObj: any) {
        this.playerId = Number(jsonObj['playerId']);
        this.kittyPlayerId = Number(jsonObj['kittyPlayerId']);
        this.attackers = jsonObj['attackers'].map(Number);
        this.defenders = jsonObj['defenders'].map(Number);
        for (const card of jsonObj.trumps) {
            this.trumps.push(new Card(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}