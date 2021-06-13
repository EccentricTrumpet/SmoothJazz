import * as src from './game.page';

describe('GamePage', () => {

  it('should resolve Trump suit', () => {
    let ranking = new src.CardRanking(3)
    ranking.resetOrder(src.Suit.CLUBS)

    let resolvedTrump = ranking.isTrump(src.cardProto(src.Suit.CLUBS, 1))
    expect(resolvedTrump).toBe(true)
  })

  it('should resolve Trump rank', () => {
    let ranking = new src.CardRanking(3)
    let resolvedTrump = ranking.isTrump(src.cardProto(src.Suit.CLUBS, 3))

    expect(resolvedTrump).toBe(true)
  })

});
