import { GamePhase, MatchPhase } from "../enums";

// Similar to BoardState but this contains non-visible states
export class StatusState {
    constructor(
        public activePlayerId = 0,
        public gamePhase = GamePhase.Draw,
        public matchPhase = MatchPhase.CREATED
    ) {}
}