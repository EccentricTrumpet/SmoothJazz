import { Seat } from "./abstractions/enums";

export class Constants {
    public static readonly cardWidth: number = 120;
    public static readonly cardHeight: number = 168;
    public static readonly cardRadius: number = 5;
    public static readonly cardOverlap: number = 25;
    public static readonly margin: number = 10;
    public static readonly seatingArrangement: {[id: number]: Seat[]} = {
        4: [Seat.South, Seat.East, Seat.North, Seat.West]
    }

    // Debugging
    public static readonly backgroundColor: string = "rgba(255, 0, 0, 0.2)";
}