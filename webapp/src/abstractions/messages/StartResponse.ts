export class StartResponse {
    activePid: number;
    cards: number;
    rank: number;

    constructor(jsonObj: any) {
        this.activePid = Number(jsonObj['activePid']);
        this.cards = Number(jsonObj['cards']);
        this.rank = Number(jsonObj['rank']);
    }
}