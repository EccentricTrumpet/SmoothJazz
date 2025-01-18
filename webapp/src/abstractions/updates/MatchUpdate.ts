import { MatchPhase } from "../enums";

export class MatchUpdate {
    phase: MatchPhase;

    constructor(jsonObj: any) {
        this.phase = jsonObj['phase'] as MatchPhase;
    }
}