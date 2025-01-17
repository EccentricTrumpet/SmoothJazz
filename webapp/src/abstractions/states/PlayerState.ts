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
        next?.pid ?? this.pid,
        next?.name ?? this.name,
        next?.level ?? this.level,
        next?.seat ?? this.seat,
        next?.hand ?? this.hand,
        next?.play ?? this.play
    )
}