import { ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { BoardState, OptionsState } from "../abstractions/states";
import { Constants } from "../Constants";
import { CardComponent } from ".";
import { FC } from "react";

interface CenterZoneInputs {
  board: BoardState;
  deckZone: Zone;
  options: OptionsState;
  controller: ControllerInterface;
}

export const CenterZone: FC<CenterZoneInputs> = ({board, deckZone, options, controller}) => {
  const cardSize = new Size(Constants.cardWidth, Constants.cardHeight);
  const discardZone = new Zone(
    new Position(
      deckZone.right() + Constants.margin,
      deckZone.top()
    ),
    cardSize
  );

  board.deck.forEach((card, i) => {
    card.state.position.x = deckZone.position.x;
    card.state.position.y = deckZone.position.y;
    card.state.offset.x = i / 3;
  });

  board.discard.forEach(card => {
    card.state.position.x = discardZone.position.x;
    card.state.position.y = discardZone.position.y;
    card.state.offset.x = 0;
    card.state.offset.y = 0;
  });

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
            left: deckZone.left() - Constants.margin - Constants.cardWidth,
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
            left: deckZone.left() - Constants.margin - Constants.cardWidth,
            top: deckZone.center().y,
            width: Constants.cardWidth,
            height: 3*Constants.margin,
            backgroundColor: Constants.backgroundColor,
          }}>
            <h4 style={{ margin: 0 }}>{board.deck.length}</h4>
          </div>
        </>
      )}
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
        <h4 style={{ margin: 0 }}>Score:</h4>
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
        <h4 style={{ margin: 0 }}>{board.score}</h4>
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
          return <CardComponent key={card.id} idx={idx} card={card} options={options} onClick={() => controller.onDraw()}/>
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
