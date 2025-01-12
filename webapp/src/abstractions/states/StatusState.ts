import { GamePhase, MatchPhase } from "../enums";

// Similar to BoardState but this contains non-visible states
export class StatusState {
    public activePlayerId: number;
    public kittyPlayerId: number;
    public trickWinnerId: number;
    public attackers: number[];
    public defenders: number[];
    public gamePhase: GamePhase;
    public matchPhase: MatchPhase;

    constructor(statusState?: StatusState) {
        this.activePlayerId = statusState?.activePlayerId ?? -1;
        this.kittyPlayerId = statusState?.kittyPlayerId ?? -1;
        this.trickWinnerId = statusState?.trickWinnerId ?? -1;
        this.attackers = statusState?.attackers ?? [];
        this.defenders = statusState?.defenders ?? [];
        this.gamePhase = statusState?.gamePhase ?? GamePhase.Draw;
        this.matchPhase = statusState?.matchPhase ?? MatchPhase.CREATED;
    }

    public withActivePlayer(activePlayerId?: number): StatusState {
        this.activePlayerId = activePlayerId ?? this.activePlayerId;
        return this;
    }

    public withTeamInfo(kittyPlayerId: number, attackers: number[], defenders: number[]): StatusState {
        this.kittyPlayerId = kittyPlayerId;
        this.attackers = attackers;
        this.defenders = defenders;
        return this;
    }

    public withWinner(trickWinnerId: number): StatusState {
        this.trickWinnerId = trickWinnerId;
        return this;
    }

    public withGamePhase(gamePhase: GamePhase): StatusState {
        this.gamePhase = gamePhase;
        return this;
    }

    public withMatchPhase(matchPhase: MatchPhase): StatusState {
        this.matchPhase = matchPhase;
        return this;
    }
}