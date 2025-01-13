export interface PlayerJsonInterface {
    pid: string,
    name: string,
    level: string,
}

export class PlayerUpdate {
    pid: number;
    name: string;
    level: number;

    constructor(jsonObj: PlayerJsonInterface) {
        this.pid = Number(jsonObj.pid);
        this.name = jsonObj.name;
        this.level = Number(jsonObj.level);
    }

    public static fromJson(jsonObj: PlayerJsonInterface): PlayerUpdate {
        return new PlayerUpdate(jsonObj);
    }
}