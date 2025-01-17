import { Seat } from "../enums";
import { Cards } from "./CardState";

export class PlayerState {
    constructor(
        public pid = -1,
        public name = "",
        public level = 2,
        public seat = Seat.South,
        public hand: Cards = [],
        public play: Cards = []
    ) {}

    public update = (next: {
        pid?: number; name?: string; level?: number; seat?: Seat; hand?: Cards; play?: Cards
    } = {}) => new PlayerState (
        this.pid = next?.pid ?? this.pid,
        this.name = next?.name ?? this.name,
        this.level = next?.level ?? this.level,
        this.seat = next?.seat ?? this.seat,
        this.hand = next?.hand ?? this.hand,
        this.play = next?.play ?? this.play
    )
}