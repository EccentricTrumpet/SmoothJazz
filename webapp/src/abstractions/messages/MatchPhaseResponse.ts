import { MatchPhase } from "../enums";

export class MatchPhaseResponse {
    matchPhase: MatchPhase;

    constructor(jsonObj: any) {
        this.matchPhase = jsonObj['phase'] as MatchPhase;
    }
}