export class CookieState {
    name: string;
    debug: boolean;
    logs: boolean;

    constructor(jsonObj?: {name?: string, debug?: boolean, logs?: boolean}) {
        this.name = jsonObj?.name || "";
        this.debug = jsonObj?.debug || false;
        this.logs = jsonObj?.logs || false;
    }
}