import { Position, Size } from ".";

export class Zone {
    constructor(
        public position: Position,
        public size: Size,
    ) {}

    top(): number {
        return this.position.y;
    }

    bottom(): number {
        return this.position.y + this.size.height;
    }

    left(): number {
        return this.position.x;
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