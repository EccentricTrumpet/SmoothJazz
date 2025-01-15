import { PlayerUpdate } from "./PlayerUpdate";
import { PlayJsonInterface, CardsUpdate } from "./CardsUpdate";

export class EndUpdate {
    play: CardsUpdate;
    kitty: CardsUpdate;
    levels = new Map<number, number>();

    constructor(jsonObj: {play: PlayJsonInterface, kitty: PlayJsonInterface, players: []}) {
        this.play = new CardsUpdate(jsonObj.play);
        this.kitty = new CardsUpdate(jsonObj.kitty);
        jsonObj.players.map(p => new PlayerUpdate(p)).forEach(p => this.levels.set(p.PID, p.level));
    }
}