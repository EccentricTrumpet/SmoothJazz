import { GamePhase, MatchPhase } from "../enums";
import { CardsState, OptionsState, TrumpState } from ".";

export class BoardState {
    public cards: CardsState;
    public trump: TrumpState;
    public options: OptionsState;
    public score: number;
    public activePID: number;
    public kittyPID: number;
    public winnerPID: number;
    public defenders: number[];
    public gamePhase: GamePhase;
    public matchPhase: MatchPhase;

    constructor(prev?: BoardState, next?: {
        cards?: CardsState;
        trump?: TrumpState;
        options?: OptionsState;
        score?: number;
        activePID?: number;
        kittyPID?: number;
        winnerPID?: number;
        defenders?: number[];
        game?: GamePhase;
        match?: MatchPhase;
    }) {
        this.cards = next?.cards ?? prev?.cards ?? new CardsState();
        this.trump = next?.trump ?? prev?.trump ?? new TrumpState();
        this.options = next?.options ?? prev?.options ?? new OptionsState();
        this.score = next?.score ?? prev?.score ?? 0
        this.activePID = next?.activePID ?? prev?.activePID ?? -1;
        this.kittyPID = next?.kittyPID ?? prev?.kittyPID ?? -1;
        this.winnerPID = next?.winnerPID ?? prev?.winnerPID ?? -1;
        this.defenders = next?.defenders ?? prev?.defenders ?? [];
        this.gamePhase = next?.game ?? prev?.gamePhase ?? GamePhase.Draw;
        this.matchPhase = next?.match ?? prev?.matchPhase ?? MatchPhase.CREATED;
    }
}