import { Vector } from ".";

export class Size {
    constructor(public width: number, public height: number) {}

    public static square = (size: number) => new Size(size, size);

    public vector = () => new Vector(this.width, this.height);
    public turn = (turn = 0) => Math.abs(turn) === 0.25 ? new Size(this.height, this.width) : this;
}