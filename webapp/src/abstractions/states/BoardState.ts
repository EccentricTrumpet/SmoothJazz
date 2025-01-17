import { CardsState, OptionsState, TrumpState } from ".";
import { GamePhase, MatchPhase } from "../enums";
import { IControl } from "../IControl";

export class BoardState {
    public control?: IControl;

    constructor(
        public cards = new CardsState(),
        public trump = new TrumpState(),
        public options = new OptionsState(),
        public score = 0,
        public activePID = -1,
        public kittyPID = -1,
        public winnerPID = -1,
        public defenders: number[] = [],
        public game = GamePhase.Draw,
        public match = MatchPhase.Created,
    ) {}

    public update = (next: {
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
    }) => new BoardState(
        next?.cards ?? this.cards,
        next?.trump ?? this.trump,
        next?.options ?? this.options,
        next?.score ?? this.score,
        next?.activePID ?? this.activePID,
        next?.kittyPID ?? this.kittyPID,
        next?.winnerPID ?? this.winnerPID,
        next?.defenders ?? this.defenders,
        next?.game ?? this.game,
        next?.match ?? this.match,
    );
}