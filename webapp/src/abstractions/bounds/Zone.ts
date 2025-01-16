import { Point, Size } from ".";

export class Zone {
    constructor(public origin: Point, public size: Size) {}
    top = () => this.origin.y;
    bottom = () => this.origin.y + this.size.height;
    left = () => this.origin.x;
    right = () => this.origin.x + this.size.width;
    center = () => new Point((this.left() + this.right())/2, (this.top() + this.bottom())/2);
    css() {
        return {
            left: this.origin.x, top: this.origin.y, width: this.size.width, height: this.size.height
        }
    }
}