import { FC, useState } from "react";
import { BackdropComponent, CardComponent, CardsZone } from ".";
import { Point, Size, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { BoardState } from "../abstractions/states";
import { Constants, Styles } from "../Constants";

export const KittyZone: FC<{ board: BoardState; deck: Zone; }> = ({board, deck}) => {
  const [displayKitty, setDisplayKitty] = useState(false);
  const toggleDisplayKitty = () => {
    board.cards.kitty.forEach(card => card.reset());
    setDisplayKitty(prevDisplayKitty => !prevDisplayKitty);
  }
  const kitty = new Zone(
    new Point(deck.left() - Constants.margin - Constants.cardWidth, deck.top()), Constants.cardSize
  );
  const displaySize = new Size(Constants.cardWidth + 9 * Constants.cardOverlap, Constants.cardHeight);
  const displayZone = new Zone(
    new Point(deck.center().x - displaySize.width/2, deck.top()), displaySize
  );

  if (!displayKitty) {
    board.cards.kitty.forEach(card => {
      card.next.origin.x = kitty.origin.x;
      card.next.origin.y = kitty.origin.y;
      card.next.delta.x = 0;
      card.next.delta.y = 0;
    });
  }

  return (
      displayKitty ? (
        <BackdropComponent onClick={toggleDisplayKitty}>
          <CardsZone cards={board.cards.kitty} seat={Seat.South} board={board} zone={displayZone} />
        </BackdropComponent>
      ) : (
        <div className="container" style={{ ...Styles.default, ...kitty.css() }}>
          { board.cards.kitty.map((card, idx) => {
            return <CardComponent key={card.id} idx={idx} card={card} options={board.options} onClick={toggleDisplayKitty} />
          })}
        </div>
      )
  );
}
