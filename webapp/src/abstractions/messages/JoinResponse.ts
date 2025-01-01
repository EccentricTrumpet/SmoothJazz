export class JoinResponse {
    id: number;
    name: string;
    level: number;

    constructor(jsonObj: any) {
        this.id = Number(jsonObj['id']);
        this.name = jsonObj['name'];
        this.level = Number(jsonObj['level']);
    }
}