export class TeamUpdate {
    kittyPID: number;
    defenders: number[];

    constructor(jsonObj: any) {
        this.kittyPID = Number(jsonObj['kittyPid']);
        this.defenders = jsonObj['defenders'].map(Number);
    }
}