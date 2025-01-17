import { FC } from "react";
import { CardComponent } from ".";
import { IControl } from "../abstractions";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { BoardState } from "../abstractions/states";
import { MARGIN, CARD_WIDTH, Styles } from "../Constants";

interface Inputs { board: BoardState; deck: Zone; control: IControl; }
export const CenterZone: FC<Inputs> = ({board, deck, control}) => {
  const trash = deck.outSet(Vector.Right.scale(MARGIN));
  const kitty = deck.outSet(Vector.Left.scale(MARGIN));
  const labelSize = new Size(CARD_WIDTH, 3*MARGIN);

  board.cards.deck.forEach((card, i) => {
    card.next.origin.set(deck.origin);
    card.next.delta.x = i / 3;
  });

  board.cards.trash.forEach(card => {
    card.next.origin.set(trash.origin);
    card.next.delta.set(Vector.Origin);
  });

  const labelCSS = (parent: Zone, delta: Vector) => {
    return { ...Styles.defaultCenter, ...parent.midSet(labelSize, delta).position() }
  }

  const labelComponent = (parent: Zone, title: string, value: number) => {
    return (
      <>
        <div className="container" style={labelCSS(parent, Vector.Up.scale(-labelSize.height/2))} >
          <h4 style={{ margin: 0 }}>{title}</h4>
        </div>
        <div className="container" style={labelCSS(parent, Vector.Down.scale(-labelSize.height/2))} >
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
    <div className="container" style={{ ...Styles.default, ...deck.position() }}>
      { board.cards.deck.map((card, i) =>
        <CardComponent key={card.id} z={i} card={card} onClick={() => control.draw()} />
      )}
    </div>
    {/* Trash */}
    <div className="container" style={{ ...Styles.default, ...trash.position() }}>
      { board.cards.trash.map((card, i) => <CardComponent key={card.id} z={i} card={card} />) }
    </div>
  </>
  ;
}
