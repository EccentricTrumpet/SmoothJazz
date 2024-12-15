export enum GamePhase {
    Draw = 0,
    Reserve = 1,    // 抓底牌
    Kitty = 2,      // 埋底牌
    Play = 3,
    End = 4,
    Waiting = 5,    // FE only state
}