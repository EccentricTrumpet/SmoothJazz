export class TeamUpdate {
    kittyPid: number;
    defenders: number[];

    constructor(jsonObj: any) {
        this.kittyPid = Number(jsonObj['kittyPid']);
        this.defenders = jsonObj['defenders'].map(Number);
    }
}