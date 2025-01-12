import { Card } from "..";

export interface PlayJsonInterface {
    pid: string, activePid: string, cards: []
}

export class PlayResponse {
    pid: number;
    cards: Card[] = [];
    activePid: number;
    winnerPid?: number;
    score?: number;

    constructor(jsonObj: PlayJsonInterface) {
        this.pid = Number(jsonObj.pid);
        this.activePid = Number(jsonObj.activePid);
        for (const card of jsonObj.cards) {
            this.cards.push(Card.fromJson(card));
        }
        if ('score' in jsonObj) {
            this.score = Number(jsonObj.score);
        }
        if ('winnerPid' in jsonObj) {
            this.winnerPid = Number(jsonObj.winnerPid);
        }
    }
}