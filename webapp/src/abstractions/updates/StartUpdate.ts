export class StartUpdate {
    activePID: number;
    cards: number;
    rank: number;

    constructor(jsonObj: any) {
        this.activePID = Number(jsonObj['activePid']);
        this.cards = Number(jsonObj['cards']);
        this.rank = Number(jsonObj['rank']);
    }
}