import { Suit } from "../enums";
import { CardInfo } from ".";

export class BidResponse {
    playerId: number;
    trumps: CardInfo[] = [];
    kittyPlayerId: number;
    attackers: number[];
    defenders: number[];

    constructor(jsonObj: any) {
        this.playerId = Number(jsonObj['playerId']);
        this.kittyPlayerId = Number(jsonObj['kittyPlayerId']);
        this.attackers = jsonObj['attackers'].map(Number);
        this.defenders = jsonObj['defenders'].map(Number);
        for (const card of jsonObj.trumps) {
            this.trumps.push(new CardInfo(
                Number(card['id']),
                card['suit'] as Suit,
                Number(card['rank'])
            ));
        }
    }
}