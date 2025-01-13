import { MatchPhase } from "../enums";

export class MatchUpdate {
    matchPhase: MatchPhase;

    constructor(jsonObj: any) {
        this.matchPhase = jsonObj['phase'] as MatchPhase;
    }
}