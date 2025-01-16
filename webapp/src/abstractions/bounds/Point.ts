export class Point {
    constructor(public x: number, public y: number) {}
    clone = () => new Point(this.x, this.y);
}