import { GamePhase } from "../enums";

// Similar to BoardState but this contains non-visible states
export class GameState {
    constructor(
        public activePlayerId = 0,
        public gamePhase = GamePhase.Draw
    ) {}
}