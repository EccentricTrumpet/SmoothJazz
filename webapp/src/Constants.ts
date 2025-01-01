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
    public static readonly backgroundColor: string = "rgba(255, 0, 0, 0.0)";

}