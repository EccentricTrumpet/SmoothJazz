import { Size } from "./abstractions/bounds";
import { Seat } from "./abstractions/enums";

export class Constants {
    // Sizes
    public static readonly cardWidth = 120;
    public static readonly cardHeight = 168;
    public static readonly cardRadius = 5;
    public static readonly cardOverlap = 25;
    public static readonly cardSize = new Size(this.cardWidth, this.cardHeight);
    public static readonly margin = 10;
    public static readonly seating: {[id: number]: Seat[]} = {
        4: [Seat.South, Seat.East, Seat.North, Seat.West]
    }

    // Status
    public static readonly statusDetails: { [id: string]: { codepoint: number, description: string } } = {
        Attacker: { codepoint: 0x1F5E1, description: "Attacking player" },
        Defender: { codepoint: 0x1F6E1, description: "Defending player" },
        Kitty: { codepoint: 0x1F431, description: "Kitty player" },
        Winner: { codepoint: 0x1F3C6, description: "Highest play of current trick" },
        2: { codepoint: 0x278B, description: "Level 2" },
        3: { codepoint: 0x278C, description: "Level 3" },
        4: { codepoint: 0x278D, description: "Level 4" },
        5: { codepoint: 0x278E, description: "Level 5" },
        6: { codepoint: 0x278F, description: "Level 6" },
        7: { codepoint: 0x2790, description: "Level 7" },
        8: { codepoint: 0x2791, description: "Level 8" },
        9: { codepoint: 0x2792, description: "Level 9" },
        10: { codepoint: 0x2793, description: "Level 10" },
        11: { codepoint: 0x1F159, description: "Level Jack" },
        12: { codepoint: 0x1F160, description: "Level Queen" },
        13: { codepoint: 0x1F15A, description: "Level King" },
        14: { codepoint: 0x1F150, description: "Level Ace" },
    }

    // Debugging
    public static readonly backgroundColor = "rgba(255, 0, 0, 0.0)";
}

export class Styles {
    public static readonly center = {
        display: "flex",
        alignItems: "center",
        justifyContent: "center"
    };
    public static readonly card = {
        width: Constants.cardWidth,
        height: Constants.cardHeight,
        borderRadius: Constants.cardRadius,
        borderStyle: "solid",
    };
    public static readonly default = {
        position: "fixed",
        maxWidth: "none",
        backgroundColor: Constants.backgroundColor
    } as React.CSSProperties;
    public static readonly window = {
        position: "fixed",
        width: "100vw",
        height: "100vh"
    } as React.CSSProperties;
}

export const seatOf = (seat: number, southSeat: number, seats: number) =>
    Constants.seating[seats][(seat + seats - southSeat) % seats];