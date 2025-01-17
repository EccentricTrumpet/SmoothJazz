import { FC } from "react";
import { CardComponent } from ".";
import { IControl } from "../abstractions";
import { Point, Size, Zone } from "../abstractions/bounds";
import { BoardState } from "../abstractions/states";
import { MARGIN, CARD_WIDTH, Styles } from "../Constants";

interface Inputs { board: BoardState; deck: Zone; control: IControl; }
export const CenterZone: FC<Inputs> = ({board, deck, control}) => {
  const discard = deck.outSet(new Point(MARGIN, 0));
  const kitty = deck.outSet(new Point(-MARGIN, 0));
  const labelSize = new Size(CARD_WIDTH, 3*MARGIN);

  board.cards.deck.forEach((card, i) => {
    card.next.origin.update(deck.origin);
    card.next.delta.x = i / 3;
  });

  board.cards.discard.forEach(card => {
    card.next.origin.update(discard.origin);
    card.next.delta.update(Point.Origin);
  });

  const labelCSS = (parent: Zone, offset: number) => {
    return { ...Styles.defaultCenter, ...parent.midSet(labelSize, new Point(0, offset)).css() }
  }

  const labelComponent = (parent: Zone, title: string, value: number) => {
    return (
      <>
        <div className="container" style={labelCSS(parent, -labelSize.height/2)} >
          <h4 style={{ margin: 0 }}>{title}</h4>
        </div>
        <div className="container" style={labelCSS(parent, labelSize.height/2)} >
          <h4 style={{ margin: 0 }}>{value}</h4>
        </div>
      </>
    );
  }

  return <>
    {/* Deck count UI */}
    { board.cards.deck.length > 0 && labelComponent(kitty, "Deck:", board.cards.deck.length) }
    {/* Score UI */}
    { labelComponent(deck, "Score:", board.score) }
    {/* Deck */}
    <div className="container" style={{ ...Styles.default, ...deck.css() }}>
      { board.cards.deck.map((card, idx) =>
        <CardComponent key={card.id} i={idx} card={card} board={board} onClick={() => control.draw()}/>
      )}
    </div>
    {/* Discard */}
    <div className="container" style={{ ...Styles.default, ...discard.css() }}>
      { board.cards.discard.map((card, idx) =>
        <CardComponent key={card.id} i={idx} card={card} board={board} />
      )}
    </div>
  </>
  ;
}
