import { FC, useState } from "react";
import { BackdropComponent, CardComponent, CardsZone } from ".";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { BoardState } from "../abstractions/states";
import { MARGIN, CARD_HEIGHT, Styles } from "../Constants";

export const KittyZone: FC<{ board: BoardState; deck: Zone; }> = ({board, deck}) => {
  const kitty = deck.outSet(Vector.Left.scale(MARGIN));
  const display = deck.midSet(new Size(2*CARD_HEIGHT, CARD_HEIGHT));
  const [displayKitty, setDisplayKitty] = useState(false);
  const toggle = () => {
    board.kitty.forEach(card => card.reset());
    setDisplayKitty(prevDisplayKitty => !prevDisplayKitty);
  }

  if (!displayKitty)
    board.kitty.forEach(card => card.next.set(kitty.origin, Vector.Origin));

  return displayKitty ?
    <BackdropComponent onClick={toggle}>
      <CardsZone cards={board.kitty} trump={board.trump} zone={display} />
    </BackdropComponent> :
    <div style={{ ...Styles.default, ...kitty.position() }}>
      { board.kitty.map((c, i) => <CardComponent key={c.id} z={i} card={c} onClick={toggle} /> )}
    </div>;
}
