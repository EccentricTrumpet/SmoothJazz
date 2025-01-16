import { FC } from "react";
import { CardComponent } from ".";
import { IControl } from "../abstractions";
import { Point, Zone } from "../abstractions/bounds";
import { BoardState } from "../abstractions/states";
import { Constants, Styles } from "../Constants";

interface Inputs { board: BoardState; deck: Zone; control: IControl; }
export const CenterZone: FC<Inputs> = ({board, deck, control}) => {
  const discardZone = new Zone(
    new Point(deck.right() + Constants.margin, deck.top()),
    Constants.cardSize
  );

  board.cards.deck.forEach((card, i) => {
    card.next.origin.x = deck.origin.x;
    card.next.origin.y = deck.origin.y;
    card.next.delta.x = i / 3;
  });

  board.cards.discard.forEach(card => {
    card.next.origin.x = discardZone.origin.x;
    card.next.origin.y = discardZone.origin.y;
    card.next.delta.x = 0;
    card.next.delta.y = 0;
  });

  return <>
    {/* Deck count UI */}
    { board.cards.deck.length > 0 && (
      <>
        <div className="container" style={{
          ...Styles.default,
          ...Styles.center,
          left: deck.left() - Constants.margin - Constants.cardWidth,
          top: deck.center().y - 3*Constants.margin,
          width: Constants.cardWidth,
          height: 3*Constants.margin,
        }}>
          <h4 style={{ margin: 0 }}>Deck:</h4>
        </div>
        <div className="container" style={{
          ...Styles.default,
          ...Styles.center,
          left: deck.left() - Constants.margin - Constants.cardWidth,
          top: deck.center().y,
          width: Constants.cardWidth,
          height: 3*Constants.margin,
        }}>
          <h4 style={{ margin: 0 }}>{board.cards.deck.length}</h4>
        </div>
      </>
    )}
    {/* Score UI */}
    <div className="container" style={{
      ...Styles.default,
      ...Styles.center,
      left: deck.left(),
      top: deck.center().y - 3*Constants.margin,
      width: Constants.cardWidth,
      height: 3*Constants.margin,
    }}>
      <h4 style={{ margin: 0 }}>Score:</h4>
    </div>
    <div className="container" style={{
      ...Styles.default,
      ...Styles.center,
      left: deck.left(),
      top: deck.center().y,
      width: Constants.cardWidth,
      height: 3*Constants.margin,
    }}>
      <h4 style={{ margin: 0 }}>{board.score}</h4>
    </div>
    {/* Deck */}
    <div className="container" style={{
      ...Styles.default,
      left: deck.left(),
      top: deck.top(),
      width: deck.size.width,
      height: deck.size.height,
    }}>
      { board.cards.deck.map((card, idx) =>
        <CardComponent key={card.id} idx={idx} card={card} options={board.options} onClick={() => control.onDraw()}/>
      )}
    </div>
    {/* Discard */}
    <div className="container" style={{ ...Styles.default, ...discardZone.css() }}>
      { board.cards.discard.map((card, idx) =>
        <CardComponent key={card.id} idx={idx} card={card} options={board.options} />
      )}
    </div>
  </>
  ;
}
