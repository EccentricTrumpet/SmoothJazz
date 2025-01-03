import { useState } from "react";
import { Position, Size, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { BoardState, OptionsState, TrumpState } from "../abstractions/states";
import { Constants } from "../Constants";
import { BackdropComponent, CardComponent, CardsZone } from ".";

interface KittyZoneInputs {
  board: BoardState;
  trumpState: TrumpState;
  options: OptionsState;
  deckZone: Zone;
}

export const KittyZone: React.FC<KittyZoneInputs> = ({board, trumpState, options, deckZone}) => {
  const [displayKitty, setDisplayKitty] = useState(false);
  const toggleDisplayKitty = () => {
    board.kitty.forEach(card => card.resetState());
    setDisplayKitty(prevDisplayKitty => !prevDisplayKitty);
  }
  const cardSize = new Size(Constants.cardWidth, Constants.cardHeight);
  const kittyZone = new Zone(
    new Position(
      deckZone.left() - Constants.margin - Constants.cardWidth,
      deckZone.top()
    ),
    cardSize
  );
  const displaySize = new Size(Constants.cardWidth + 9 * Constants.cardOverlap, Constants.cardHeight);
  const displayZone = new Zone(
    new Position(
      deckZone.center().x - displaySize.width/2,
      deckZone.top()
    ),
    displaySize
  );

  if (!displayKitty) {
    board.kitty.forEach(card => {
      card.state.position.x = kittyZone.position.x;
      card.state.position.y = kittyZone.position.y;
      card.state.offset.x = 0;
      card.state.offset.y = 0;
    });
  }

  return (
      displayKitty ? (
        <BackdropComponent onClick={toggleDisplayKitty}>
          <CardsZone cards={board.kitty} seat={Seat.South} trumpState={trumpState} zone={displayZone} options={options} />
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
          { board.kitty.map((card, idx) => {
            return <CardComponent key={card.id} idx={idx} card={card} options={options} onClick={toggleDisplayKitty} />
          })}
        </div>
      )
  );
}
