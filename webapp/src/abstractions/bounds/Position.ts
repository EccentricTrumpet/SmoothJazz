export class Position {
    constructor(public x: number, public y: number) {}
    clone = () => new Position(this.x, this.y);
}