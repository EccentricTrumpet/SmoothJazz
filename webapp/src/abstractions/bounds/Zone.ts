import { Vector, Size } from ".";

export class Zone {
    constructor(public origin: Vector, public size: Size) {}

    // Bounds and references
    top = () => this.origin.y;
    bottom = () => this.origin.y + this.size.height;
    left = () => this.origin.x;
    right = () => this.origin.x + this.size.width;
    center = () => this.origin.add(this.size.vector().scale(0.5));

    // Transform into css position properties
    position = () => ({ left: this.origin.x, top: this.origin.y, ...this.size.properties() });

    // Offsets, create a new zone using offsets from the current one

    // Offset using the zone center as a reference
    midSet = (size = this.size, v = Vector.Origin) =>
        new Zone(this.center().add(v).add(size.vector().scale(-0.5)), size);

    // Offset inwards from the zone boundary
    // x => x < 0: inset by x from right, > 0: inset by x from left, 0: maintain center in x axis
    // y => y < 0: inset by y from bottom, y > 0: inset by y from top, 0: maintain center in y axis
    inSet(v = Vector.Origin, size = this.size) {
        let x = v.x, y = v.y, mid = this.center();
        x += v.x < 0 ? this.right() - size.width : v.x > 0 ? this.left() : mid.x - size.width/2;
        y += v.y < 0 ? this.bottom() - size.height : v.y > 0 ? this.top() : mid.y - size.height/2;
        return new Zone(new Vector(x, y), size);
    }

    // Offset outwards from the zone boundary
    // x => < 0: outset by x from left, > 0: outset by x from right, 0: maintain center in x axis
    // y => < 0: outset by y from top, y > 0: outset by y from bottom, 0: maintain center in y axis
    outSet(v = Vector.Origin, size = this.size) {
        let x = v.x, y = v.y, mid = this.center();
        x += v.x < 0 ? this.left() - size.width : v.x > 0 ? this.right() : mid.x - size.width/2;
        y += v.y < 0 ? this.top() - size.height : v.y > 0 ? this.bottom() : mid.y - size.height/2;
        return new Zone(new Vector(x, y), size);
    }
}