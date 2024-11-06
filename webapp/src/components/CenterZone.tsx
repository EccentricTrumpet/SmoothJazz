import { ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { BoardState, OptionsState } from "../abstractions/states";
import { Constants } from "../Constants";
import { CardComponent } from ".";

interface CenterZoneInputs {
  board: BoardState;
  deckZone: Zone;
  options: OptionsState;
  controller: ControllerInterface;
}

export const CenterZone: React.FC<CenterZoneInputs> = ({board, deckZone, options, controller}) => {
  const cardSize = new Size(Constants.cardWidth, Constants.cardHeight);
  const kittyZone = new Zone(
    new Position(
      deckZone.left() - Constants.margin - Constants.cardWidth,
      deckZone.top()
    ),
    cardSize
  );
  const discardZone = new Zone(
    new Position(
      deckZone.right() + Constants.margin,
      deckZone.top()
    ),
    cardSize
  );

  for (let card of board.deck) {
    card.state.position.x = deckZone.position.x;
    card.state.position.y = deckZone.position.y;
    if (card.prevState) {
      card.prevState.position.x = deckZone.position.x;
      card.prevState.position.y = deckZone.position.y;
    }
  }

  return (
    <>
      {/* Score UI */}
      <div className="container" style={{
        position: "fixed",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        left: deckZone.left(),
        top: deckZone.center().y - 2*Constants.margin,
        width: Constants.cardWidth,
        height: 2*Constants.margin,
        backgroundColor: Constants.backgroundColor,
      }}>
        <h4 style={{ margin: 0 }}>Points:</h4>
      </div>
      <div className="container" style={{
        position: "fixed",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        left: deckZone.left(),
        top: deckZone.center().y,
        width: Constants.cardWidth,
        height: 2*Constants.margin,
        backgroundColor: Constants.backgroundColor,
      }}>
        <h4 style={{ margin: 0 }}>{board.points}</h4>
      </div>
      {/* Kitty */}
      <div className="container" style={{
        position: "fixed",
        left: kittyZone.left(),
        top: kittyZone.top(),
        width: kittyZone.size.width,
        height: kittyZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        { board.kitty.map((card, idx) => {
          return <CardComponent idx={idx} card={card} options={options} />
        })}
      </div>
      {/* Deck */}
      <div className="container" style={{
        position: "fixed",
        left: deckZone.left(),
        top: deckZone.top(),
        width: deckZone.size.width,
        height: deckZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        { board.deck.map((card, idx) => {
          return <CardComponent key={card.id} idx={idx} card={card} options={options} onClick={() => {
            controller.onDrawCard(card);
          }}/>
        })}
      </div>
      {/* Discard */}
      <div className="container" style={{
        position: "fixed",
        left: discardZone.left(),
        top: discardZone.top(),
        width: discardZone.size.width,
        height: discardZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        { board.discard.map((card, idx) => {
          return <CardComponent idx={idx} card={card} options={options} />
        })}
      </div>
    </>
  );
}
