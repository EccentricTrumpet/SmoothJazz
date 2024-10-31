import { Constants } from "../Constants";
import { Zone } from "../abstractions/Zone";
import { IController } from "../abstractions/IController";
import { Size } from "../abstractions/Size";
import { Position } from "../abstractions/Position";
import CardComponent from "./CardComponent";
import { DisplaySettings } from "../abstractions/DisplaySettings";
import { BoardState } from "../abstractions/BoardState";
import { CardState } from "../abstractions/CardState";
import { SeatPosition } from "../abstractions/SeatPosition";


interface CenterZoneArgument {
  board: BoardState;
  parentZone: Zone;
  settings: DisplaySettings;
  controller: IController;
}

const ControlZone: React.FC<CenterZoneArgument> = ({board, parentZone, settings, controller}) => {

  const cardSize = new Size(Constants.cardWidth, Constants.cardHeight);
  const deckZone = new Zone(
    new Position(
      parentZone.center().x - Constants.cardWidth/2,
      parentZone.center().y - Constants.cardHeight/2
    ),
    cardSize
  );
  const kittyZone = new Zone(
    new Position(
      deckZone.position.x - Constants.margin - Constants.cardWidth,
      deckZone.position.y
    ),
    cardSize
  );
  const discardZone = new Zone(
    new Position(
      deckZone.right() + Constants.margin,
      deckZone.position.y
    ),
    cardSize
  );

  for (let card of board.deck) {
    card.state = new CardState(false, false, 0, deckZone.position);
  }

  return (
    <>
      {/* Score UI */}
      <div className="container" style={{
        position: "fixed",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        left: deckZone.position.x,
        top: parentZone.center().y - 2*Constants.margin,
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
        left: deckZone.position.x,
        top: parentZone.center().y,
        width: Constants.cardWidth,
        height: 2*Constants.margin,
        backgroundColor: Constants.backgroundColor,
      }}>
        <h4 style={{ margin: 0 }}>{board.points}</h4>
      </div>
      {/* Kitty */}
      <div className="container" style={{
        position: "fixed",
        left: kittyZone.position.x,
        top: kittyZone.position.y,
        width: kittyZone.size.width,
        height: kittyZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        { board.kitty.map((card, idx) => {
          return <CardComponent idx={idx} card={card} settings={settings} />
        })}
      </div>
      {/* Deck */}
      <div className="container" style={{
        position: "fixed",
        left: deckZone.position.x,
        top: deckZone.position.y,
        width: deckZone.size.width,
        height: deckZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        { board.deck.map((card, idx) => {
          return <CardComponent key={card.id} idx={idx} card={card} settings={settings} onClick={() => {
            controller.onDrawCard(card);
          }}/>
        })}
      </div>
      {/* Discard */}
      <div className="container" style={{
        position: "fixed",
        left: discardZone.position.x,
        top: discardZone.position.y,
        width: discardZone.size.width,
        height: discardZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        { board.discard.map((card, idx) => {
          return <CardComponent idx={idx} card={card} settings={settings} />
        })}
      </div>
    </>
  );
}

export default ControlZone;
