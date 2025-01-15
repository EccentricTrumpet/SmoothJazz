import { FC, useState } from "react";
import { Position, Size, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { BoardState } from "../abstractions/states";
import { Constants } from "../Constants";
import { BackdropComponent, CardComponent, CardsZone } from ".";

interface Inputs { board: BoardState; deckZone: Zone; }
export const KittyZone: FC<Inputs> = ({board, deckZone}) => {
  const [displayKitty, setDisplayKitty] = useState(false);
  const toggleDisplayKitty = () => {
    board.cards.kitty.forEach(card => card.reset());
    setDisplayKitty(prevDisplayKitty => !prevDisplayKitty);
  }

  const cardSize = new Size(Constants.cardWidth, Constants.cardHeight);
  const kittyZone = new Zone(
    new Position(deckZone.left() - Constants.margin - Constants.cardWidth, deckZone.top()), cardSize
  );
  const displaySize = new Size(Constants.cardWidth + 9 * Constants.cardOverlap, Constants.cardHeight);
  const displayZone = new Zone(
    new Position(deckZone.center().x - displaySize.width/2, deckZone.top()), displaySize
  );

  if (!displayKitty) {
    board.cards.kitty.forEach(card => {
      card.next.position.x = kittyZone.position.x;
      card.next.position.y = kittyZone.position.y;
      card.next.offset.x = 0;
      card.next.offset.y = 0;
    });
  }

  return (
      displayKitty ? (
        <BackdropComponent onClick={toggleDisplayKitty}>
          <CardsZone cards={board.cards.kitty} seat={Seat.South} board={board} zone={displayZone} />
        </BackdropComponent>
      ) : (
        <div className="container" style={{
          position: "fixed",
          left: kittyZone.left(),
          top: kittyZone.top(),
          width: kittyZone.size.width,
          height: kittyZone.size.height,
          backgroundColor: Constants.backgroundColor,
        }}>
          { board.cards.kitty.map((card, idx) => {
            return <CardComponent key={card.id} idx={idx} card={card} options={board.options} onClick={toggleDisplayKitty} />
          })}
        </div>
      )
  );
}
