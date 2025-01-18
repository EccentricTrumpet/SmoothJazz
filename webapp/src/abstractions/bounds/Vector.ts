export class Vector {
    static readonly Origin = new Vector(0, 0);
    static readonly Left = new Vector(-1, 0);
    static readonly Right = new Vector(1, 0);
    static readonly Up = new Vector(0, -1);
    static readonly Down = new Vector(0, 1);

    constructor(public x: number, public y: number) {}

    scale = (scale: number) => new Vector(this.x*scale, this.y*scale);
    times = (delta: Vector) => new Vector(this.x*delta.x, this.y*delta.y);
    add = (delta: Vector) => new Vector(this.x + delta.x, this.y + delta.y);
    position = () => ({ x: this.x, y: this.y });
    clone = () => new Vector(this.x, this.y);

    set(next: Vector) { this.x = next.x; this.y = next.y; }
}