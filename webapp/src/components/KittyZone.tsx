import { FC, useState } from "react";
import { BackdropComponent, CardComponent, CardsZone } from ".";
import { Point, Size, Zone } from "../abstractions/bounds";
import { BoardState } from "../abstractions/states";
import { MARGIN, CARD_HEIGHT, Styles } from "../Constants";
import { Seat } from "../abstractions/enums";

export const KittyZone: FC<{ board: BoardState; deck: Zone; }> = ({board, deck}) => {
  const kitty = deck.outSet(new Point(-MARGIN, 0));
  const display = deck.midSet(new Size(2*CARD_HEIGHT, CARD_HEIGHT));
  const [displayKitty, setDisplayKitty] = useState(false);
  const toggleKitty = () => {
    board.cards.kitty.forEach(card => card.reset());
    setDisplayKitty(prevDisplayKitty => !prevDisplayKitty);
  }

  if (!displayKitty) {
    board.cards.kitty.forEach(card => {
      card.next.origin.update(kitty.origin);
      card.next.delta.update(Point.Origin);
    });
  }

  return (
    displayKitty ? (
      <BackdropComponent onClick={toggleKitty}>
        <CardsZone cards={board.cards.kitty} board={board} zone={display} seat={Seat.South} />
      </BackdropComponent>
    ) : (
      <div className="container" style={{ ...Styles.default, ...kitty.css() }}>
        { board.cards.kitty.map((card, idx) => {
          return <CardComponent key={card.id} i={idx} card={card} board={board} onClick={toggleKitty} />
        })}
      </div>
    )
  );
}
