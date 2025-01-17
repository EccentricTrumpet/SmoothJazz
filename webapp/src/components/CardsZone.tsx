import { FC } from "react";
import { CardComponent } from ".";
import { Vector, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { IControl } from "../abstractions/IControl";
import { Cards, TrumpState, } from "../abstractions/states";
import { CARD_MARGIN, CARD_SIZE, CARD_WIDTH, Styles } from "../Constants";

const settings: { [id in Seat]: { turn: number, pick: Vector, delta: Vector, z: number } } = {
  [Seat.East]: { turn: -0.25, pick: Vector.Left.scale(CARD_MARGIN), delta: Vector.Up, z: 1 },
  [Seat.South]: { turn: 0, pick: Vector.Up.scale(CARD_MARGIN), delta: Vector.Right, z: 1 },
  [Seat.West]: { turn: 0.25, pick: Vector.Right.scale(CARD_MARGIN), delta: Vector.Down, z: 1 },
  [Seat.North]: { turn: 0, pick: Vector.Down.scale(CARD_MARGIN), delta: Vector.Right, z: -1 },
}

interface Inputs { cards: Cards; trump: TrumpState; zone: Zone; seat?: Seat; control?: IControl; }
export const CardsZone: FC<Inputs> = ({cards, trump, zone, seat = Seat.South, control}) => {
  // Sort cards for display
  cards.sort((a, b) => trump.orderOf(a) - trump.orderOf(b));
  const { turn, pick, delta, z } = settings[seat];

  const maxRange = turn === 0 ? zone.size.width : zone.size.height;
  const range = Math.min(maxRange, CARD_MARGIN*(cards.length - 1) + CARD_WIDTH);
  const offset = CARD_SIZE.vector().add(new Vector(-CARD_WIDTH, -CARD_WIDTH).times(delta));
  const start = zone.center().add(delta.scale(range).add(offset).scale(-0.5));
  const margin = Math.min(CARD_MARGIN, (range - CARD_WIDTH)/Math.max(cards.length-1, 1));

  for (let i = 0; i < cards.length; i++) {
    cards[i].next.turn = turn;
    cards[i].next.origin = start.add(delta.scale(i*margin));
    cards[i].next.delta.set(cards[i].next.picked ? pick : Vector.Origin);
  }

  return (
    <div className="container" style={{ ...Styles.default, ...zone.position() }}>
      { cards.map((c, i) =>
        <CardComponent key={c.id} z={i*z} card={c} onClick={() => control?.pick(c)} />
      )}
    </div>
  );
}
