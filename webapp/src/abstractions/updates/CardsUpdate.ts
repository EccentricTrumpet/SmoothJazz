import { Card } from "..";
import { GamePhase } from "../enums";

export interface PlayJsonInterface { pid: string, cards: [] }

export class CardsUpdate {
    pid: number;
    cards: Card[] = [];
    nextPID?: number;
    hintPID?: number;
    phase?: GamePhase;
    score?: number;

    constructor(jsonObj: PlayJsonInterface) {
        this.pid = Number(jsonObj.pid);
        jsonObj.cards.map(Card.fromJson).forEach(c => this.cards.push(c));
        if ('nextPID' in jsonObj) { this.nextPID = Number(jsonObj.nextPID); }
        if ('hintPID' in jsonObj) { this.hintPID = Number(jsonObj.hintPID); }
        if ('phase' in jsonObj) { this.phase = jsonObj.phase as GamePhase; }
        if ('score' in jsonObj) { this.score = Number(jsonObj.score); }
    }
}