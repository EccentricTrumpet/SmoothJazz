import { FC } from "react";
import { CardComponent } from ".";
import { Point, Size, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { IControl } from "../abstractions/IControl";
import { BoardState, Cards, } from "../abstractions/states";
import { CARD_HEIGHT, CARD_MARGIN, CARD_WIDTH, Styles } from "../Constants";

const settings: { [id in Seat]: { rotate: number, selected: Point, delta: Point, index: number } } = {
  [Seat.East]: { rotate: -90, selected: new Point(-CARD_MARGIN, 0), delta: new Point(0, -1), index: 1 },
  [Seat.South]: { rotate: 0, selected: new Point(0, -CARD_MARGIN), delta: new Point(1, 0), index: 1 },
  [Seat.West]: { rotate: 90, selected: new Point(CARD_MARGIN, 0), delta: new Point(0, 1), index: 1 },
  [Seat.North]: { rotate: 0, selected: new Point(0, CARD_MARGIN), delta: new Point(1, 0), index: -1 },
}

interface Inputs { cards: Cards; seat: Seat; board: BoardState; zone: Zone; control?: IControl; }
export const CardsZone: FC<Inputs> = ({cards, seat, board, zone, control = undefined}) => {
  // Sort cards for display
  cards.sort((a, b) => board.trump.orderOf(a) - board.trump.orderOf(b));
  const { rotate, selected, delta, index } = settings[seat];

  const maxRange = rotate === 0 ? zone.size.width : zone.size.height;
  const range = Math.min(maxRange, CARD_MARGIN*(cards.length - 1) + CARD_WIDTH);
  const offset = new Point(CARD_WIDTH, CARD_HEIGHT).plus(new Point(CARD_WIDTH, CARD_WIDTH).dot(delta).scale(-1));
  const start = zone.center().plus(offset.scale(-0.5)).plus(delta.scale(-range/2));
  const margin = Math.min(CARD_MARGIN, (range - CARD_WIDTH)/Math.max(cards.length-1, 1));

  for (let i = 0; i < cards.length; i++) {
    cards[i].next.rotate = rotate;
    cards[i].next.origin = start.plus(delta.scale(i*margin));
    cards[i].next.delta.update(cards[i].next.selected ? selected : Point.Origin);
  }

  return (
    <div className="container" style={{ ...Styles.default, ...zone.css() }}>
      { cards.map((c, i) =>
        <CardComponent key={c.id} i={i*index} card={c} board={board} onClick={() => control?.select(c)} />
      )}
    </div>
  );
}
