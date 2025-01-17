export class Size {
    constructor(public width: number, public height: number) {}

    public rotate (degrees = 0) {
        return degrees === 90 || degrees === -90 ? new Size(this.height, this.width) : this;
    }
    public static square = (size: number) => new Size(size, size);
}