import { Point, Size } from ".";

export class Zone {
    constructor(public origin: Point, public size: Size) {}

    // Bounds and references
    top = () => this.origin.y;
    bottom = () => this.origin.y + this.size.height;
    left = () => this.origin.x;
    right = () => this.origin.x + this.size.width;
    center = () => new Point((this.left() + this.right())/2, (this.top() + this.bottom())/2);

    // Offsets, create a new zone using offsets from the current one

    // Offset using the zone center as a reference
    public midSet(size = this.size, delta = Point.Origin) {
        return new Zone(new Point(
            this.center().x - size.width/2 + delta.x,
            this.center().y - size.height/2 + delta.y
        ), size);
    }

    // Offset inwards from the zone boundary
    // x => x < 0: inset by x from right, > 0: inset by x from left, 0: maintain center in x axis
    // y => y < 0: inset by y from bottom, y > 0: inset by y from top, 0: maintain center in y axis
    public inSet(delta = Point.Origin, size = this.size) {
        let x = delta.x, y = delta.y;
        x += delta.x < 0 ? this.right() - size.width : delta.x > 0 ? this.left() : this.center().x - size.width/2;
        y += delta.y < 0 ? this.bottom() - size.height : delta.y > 0 ? this.top() : this.center().y - size.height/2;
        return new Zone(new Point(x, y), size);
    }

    // Offset outwards from the zone boundary
    // x => < 0: outset by x from left, > 0: outset by x from right, 0: maintain center in x axis
    // y => < 0: outset by y from top, y > 0: outset by y from bottom, 0: maintain center in y axis
    public outSet(delta = Point.Origin, size = this.size) {
        let x = delta.x, y = delta.y;
        x += delta.x < 0 ? this.left() - size.width : delta.x > 0 ? this.right() : this.center().x - size.width/2;
        y += delta.y < 0 ? this.top() - size.height : delta.y > 0 ? this.bottom() : this.center().y - size.height/2;
        return new Zone(new Point(x, y), size);
    }

    // Transform into css properties
    public css() { return {
        left: this.origin.x, top: this.origin.y, width: this.size.width, height: this.size.height
    } }
}