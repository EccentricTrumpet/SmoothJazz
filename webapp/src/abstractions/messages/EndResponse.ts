import { GamePhase} from "../enums";
import { PlayerUpdate } from "./PlayerUpdate";
import { PlayJsonInterface, PlayResponse } from "./PlayResponse";

export class EndResponse {
    play: PlayResponse;
    kitty: PlayResponse;
    phase: GamePhase;
    players: Map<number, number>;

    constructor(jsonObj: {play: PlayJsonInterface, kitty: PlayJsonInterface, phase: unknown, players: []}) {
        this.play = new PlayResponse(jsonObj.play);
        this.kitty = new PlayResponse(jsonObj.kitty);
        this.phase = jsonObj.phase as GamePhase;
        this.players = new Map<number, number>();
        const players = jsonObj.players.map(PlayerUpdate.fromJson);
        for (const player of players) {
            this.players.set(player.id, player.level);
        }
    }
}