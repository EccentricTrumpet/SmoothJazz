import * as src from './game.page';

describe('GamePage', () => {

  it('should resolve Trump suit', () => {
    let ranking = new src.CardRanking(3)
    ranking.resetOrder(src.Suit.Clubs)

    let resolvedTrump = ranking.getFunctionalSuit(new src.Card(src.Suit.Clubs, 1))
    expect(resolvedTrump).toBe(src.Suit.Trump)
  })

  it('should resolve Trump rank', () => {
    let ranking = new src.CardRanking(3)
    let resolvedTrump = ranking.getFunctionalSuit(new src.Card(src.Suit.Clubs, 3))

    expect(resolvedTrump).toBe(src.Suit.Trump)
  })

});
