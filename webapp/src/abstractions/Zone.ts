import { Position } from "./Position";
import { Size } from "./Size";

export class Zone {
    constructor(
        public position: Position,
        public size: Size,
    ) {}

    bottom(): number {
        return this.position.y + this.size.height;
    }

    right(): number {
        return this.position.x + this.size.width;
    }

    center(): Position {
        return new Position(
            this.position.x + this.size.width/2,
            this.position.y + this.size.height/2,
        )
    }
}