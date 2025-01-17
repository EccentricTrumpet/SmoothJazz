export class Point {
    public static readonly Origin = new Point(0, 0);

    constructor(public x: number, public y: number) {}
    clone = () => new Point(this.x, this.y);
    scale = (scale: number) => new Point(this.x*scale, this.y*scale);
    dot = (delta: Point) => new Point(this.x*delta.x, this.y*delta.y);
    plus = (delta: Point) => new Point(this.x + delta.x, this.y + delta.y);
    update(next: Point) { this.x = next.x; this.y = next.y; }
}