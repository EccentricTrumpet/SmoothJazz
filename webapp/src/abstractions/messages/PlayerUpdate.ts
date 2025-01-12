export interface PlayerJsonInterface {
    id: string,
    name: string,
    level: string,
}

export class PlayerUpdate {
    id: number;
    name: string;
    level: number;

    constructor(jsonObj: PlayerJsonInterface) {
        this.id = Number(jsonObj.id);
        this.name = jsonObj.name;
        this.level = Number(jsonObj.level);
    }

    public static fromJson(jsonObj: PlayerJsonInterface): PlayerUpdate {
        return new PlayerUpdate(jsonObj);
    }
}