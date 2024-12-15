export class JoinResponse {
    id: number;
    name: string;

    constructor(jsonObj: any) {
        this.id = Number(jsonObj['id']);
        this.name = jsonObj['name'];
    }
}