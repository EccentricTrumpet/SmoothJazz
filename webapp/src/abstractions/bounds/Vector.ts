export class Vector {
    public static readonly Origin = new Vector(0, 0);
    public static readonly Left = new Vector(-1, 0);
    public static readonly Right = new Vector(1, 0);
    public static readonly Up = new Vector(0, -1);
    public static readonly Down = new Vector(0, 1);

    constructor(public x: number, public y: number) {}

    scale = (scale: number) => new Vector(this.x*scale, this.y*scale);
    times = (delta: Vector) => new Vector(this.x*delta.x, this.y*delta.y);
    add = (delta: Vector) => new Vector(this.x + delta.x, this.y + delta.y);
    set(next: Vector) { this.x = next.x; this.y = next.y; }

    clone = () => new Vector(this.x, this.y);
    position() { return { x: this.x, y: this.y } }
}