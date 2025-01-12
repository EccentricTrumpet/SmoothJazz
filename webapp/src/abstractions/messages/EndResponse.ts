import { PlayerUpdate } from "./PlayerUpdate";
import { PlayJsonInterface, PlayResponse } from "./PlayResponse";

export class EndResponse {
    play: PlayResponse;
    kitty: PlayResponse;
    players = new Map<number, number>();

    constructor(jsonObj: {play: PlayJsonInterface, kitty: PlayJsonInterface, players: []}) {
        this.play = new PlayResponse(jsonObj.play);
        this.kitty = new PlayResponse(jsonObj.kitty);
        const players = jsonObj.players.map(PlayerUpdate.fromJson);
        for (const player of players) {
            this.players.set(player.id, player.level);
        }
    }
}