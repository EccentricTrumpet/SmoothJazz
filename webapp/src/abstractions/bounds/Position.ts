export class Position {
    constructor(
        public x: number,
        public y: number
    ) {}

    clone(): Position {
        return new Position(this.x, this.y);
    }
}