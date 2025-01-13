import { PlayerUpdate } from "./PlayerUpdate";
import { PlayJsonInterface, CardsUpdate } from "./CardsUpdate";

export class EndUpdate {
    play: CardsUpdate;
    kitty: CardsUpdate;
    players = new Map<number, number>();

    constructor(jsonObj: {play: PlayJsonInterface, kitty: PlayJsonInterface, players: []}) {
        this.play = new CardsUpdate(jsonObj.play);
        this.kitty = new CardsUpdate(jsonObj.kitty);
        const players = jsonObj.players.map(PlayerUpdate.fromJson);
        for (const player of players) {
            this.players.set(player.pid, player.level);
        }
    }
}