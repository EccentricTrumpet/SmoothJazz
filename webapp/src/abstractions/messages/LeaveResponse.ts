export class LeaveResponse {
    id: number;

    constructor(jsonObj: any) {
        this.id = Number(jsonObj['id']);
    }
}