import { CardState } from "./CardState";
import { Seat } from "../enums";

export class PlayerState {
    public pid: number;
    public name: string;
    public level: number;
    public seat: Seat;
    public hand: CardState[];
    public play: CardState[];

    constructor(
        prev?: PlayerState,
        next?: { pid?: number, name?: string, level?: number, seat?: Seat, hand?: CardState[], play?: CardState[] }
    ) {
        this.pid = next?.pid ?? prev?.pid ?? -1;
        this.name = next?.name ?? prev?.name ?? "";
        this.level = next?.level ?? prev?.level ?? 2;
        this.seat = next?.seat ?? prev?.seat ?? Seat.South;
        this.hand = next?.hand ?? prev?.hand ?? [];
        this.play = next?.play ?? prev?.play ?? [];
    }
}