import { Vector } from ".";

export class Size {
    constructor(public width: number, public height: number) {}

    static square = (size: number) => new Size(size, size);

    vector = () => new Vector(this.width, this.height);
    turn = (turn = 0) => Math.abs(turn) === 0.25 ? new Size(this.height, this.width) : this;
    css() { return { width: this.width, height: this.height }; }
}