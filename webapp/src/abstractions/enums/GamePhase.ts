export enum GamePhase {
    Draw = 0,
    Kitty = 1,      // 埋底牌
    Play = 2,
    End = 3,
    Waiting = 4,    // FE only state
}