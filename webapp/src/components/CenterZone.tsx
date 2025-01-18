import { FC } from "react";
import { CardComponent } from ".";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { BoardState } from "../abstractions/states";
import { MARGIN, CARD_WIDTH, Styles } from "../Constants";

interface Inputs { board: BoardState; deck: Zone; }
export const CenterZone: FC<Inputs> = ({board, deck}) => {
  const trash = deck.outSet(Vector.Right.scale(MARGIN));
  const kitty = deck.outSet(Vector.Left.scale(MARGIN));
  const labelSize = new Size(CARD_WIDTH, 3*MARGIN);

  board.deck.forEach((card, i) => card.next.set(deck.origin, new Vector(i/3, 0)));
  board.trash.forEach(card => card.next.set(trash.origin, Vector.Origin));

  const labelCSS = (parent: Zone, delta: Vector) =>
    ({ ...Styles.defaultCenter, ...parent.midSet(labelSize, delta).position() })

  const labelComponent = (parent: Zone, title: string, value: number) =>
    (<>
      <div style={labelCSS(parent, Vector.Up.scale(-labelSize.height/2))} >
        <h4 style={{ margin: 0 }}>{title}</h4>
      </div>
      <div style={labelCSS(parent, Vector.Down.scale(-labelSize.height/2))} >
        <h4 style={{ margin: 0 }}>{value}</h4>
      </div>
    </>);


  return <>
    { board.deck.length > 0 && labelComponent(kitty, "Deck:", board.deck.length) }
    { labelComponent(deck, "Score:", board.score) }
    <div style={{ ...Styles.default, ...deck.position() }}>
      { board.deck.map((card, i) =>
        <CardComponent key={card.id} z={i} card={card} onClick={() => board.control?.draw()} />
      )}
    </div>
    <div style={{ ...Styles.default, ...trash.position() }}>
      { board.trash.map((card, i) => <CardComponent key={card.id} z={i} card={card} />) }
    </div>
  </>
}
