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

  for (let card of board.kitty) {
    card.state.position.x = kittyZone.position.x;
    card.state.position.y = kittyZone.position.y;
    card.state.offset.x = 0;
    card.state.offset.y = 0;
  }

  for (let card of board.deck) {
    card.state.position.x = deckZone.position.x;
    card.state.position.y = deckZone.position.y;
    if (card.prevState) {
      card.prevState.position.x = deckZone.position.x;
      card.prevState.position.y = deckZone.position.y;
    }
  }

  for (let card of board.discard) {
    card.state.position.x = discardZone.position.x;
    card.state.position.y = discardZone.position.y;
  }

  return (
    <>
      {/* Deck count UI */}
      { board.deck.length > 0 && (
        <>
          <div className="container" style={{
            position: "fixed",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            left: kittyZone.left(),
            top: deckZone.center().y - 3*Constants.margin,
            width: Constants.cardWidth,
            height: 3*Constants.margin,
            backgroundColor: Constants.backgroundColor,
          }}>
            <h4 style={{ margin: 0 }}>Deck:</h4>
          </div>
          <div className="container" style={{
            position: "fixed",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            left: kittyZone.left(),
            top: deckZone.center().y,
            width: Constants.cardWidth,
            height: 3*Constants.margin,
            backgroundColor: Constants.backgroundColor,
          }}>
            <h4 style={{ margin: 0 }}>{board.deck.length}</h4>
          </div>
        </>
      )}
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
          return <CardComponent key={card.id} idx={idx} card={card} options={options} />
        })}
      </div>
      {/* Score UI */}
      <div className="container" style={{
        position: "fixed",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        left: deckZone.left(),
        top: deckZone.center().y - 3*Constants.margin,
        width: Constants.cardWidth,
        height: 3*Constants.margin,
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
        height: 3*Constants.margin,
        backgroundColor: Constants.backgroundColor,
      }}>
        <h4 style={{ margin: 0 }}>{board.points}</h4>
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
            controller.onDraw();
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
          return <CardComponent key={card.id} idx={idx} card={card} options={options} />
        })}
      </div>
    </>
  );
}
