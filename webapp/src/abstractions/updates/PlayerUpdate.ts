export class PlayerUpdate {
    PID: number;
    name: string;
    level: number;

    constructor(jsonObj: { pid: string, name: string, level: string }) {
        this.PID = Number(jsonObj.pid);
        this.name = jsonObj.name;
        this.level = Number(jsonObj.level);
    }
}