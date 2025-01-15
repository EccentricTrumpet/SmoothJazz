import { Position, Size } from ".";

export class Zone {
    constructor(public position: Position, public size: Size) {}
    top = () => this.position.y;
    bottom = () => this.position.y + this.size.height;
    left = () => this.position.x;
    right = () => this.position.x + this.size.width;
    center = () => new Position(
        this.position.x + this.size.width/2,
        this.position.y + this.size.height/2,
    );
}