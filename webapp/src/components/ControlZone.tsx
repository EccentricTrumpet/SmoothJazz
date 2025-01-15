import { FC } from "react";
import { Constants } from "../Constants";
import { ControlInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase } from "../abstractions/enums";
import { BoardState } from "../abstractions/states";

interface Inputs { parentZone: Zone; board: BoardState; control: ControlInterface; }
export const ControlZone: FC<Inputs> = ({parentZone, board, control}) => {
  const zone = new Zone(
    new Position(
      parentZone.left() + parentZone.size.width - Constants.margin - Constants.cardHeight,
      parentZone.top() + parentZone.size.height - Constants.margin - Constants.cardHeight,
    ),
    new Size(Constants.cardHeight, Constants.cardHeight)
  );

  let buttonText = "";
  let buttonAction = () => {};
  let buttonDisabled = false;

  switch(board.matchPhase) {
    case MatchPhase.CREATED:
      buttonText = "Leave";
      buttonAction = () => control.onLeave();
      break;
    case MatchPhase.STARTED:
      switch(board.gamePhase) {
        case GamePhase.Draw:
          buttonText = "Bid";
          buttonAction = () => control.onBid();
          break;
        case GamePhase.Kitty:
          buttonText = "Hide";
          buttonAction = () => control.onHide();
          break;
        case GamePhase.Play:
          buttonText = "Play";
          buttonAction = () => control.onPlay();
          break;
        case GamePhase.End:
          buttonText = "Next Game";
          buttonAction = () => control.onNext();
          break;
        case GamePhase.Waiting:
          buttonText = "Waiting...";
          buttonDisabled = true;
          break;
      }
      break;
  }

  return (
    <div className="container" style={{
      position: "fixed",
      left: zone.left(),
      top: zone.top(),
      width: zone.size.width,
      height: zone.size.height,
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      backgroundColor: Constants.backgroundColor,
    }}>
      {buttonText && buttonText.length > 0 && (
        <button
          className={(buttonDisabled) ? "disabled" : ""}
          onClick={buttonAction}
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            opacity: buttonDisabled ? "0.4" : "1.0"
          }}>
          {buttonText}
        </button>
      )}
    </div>
  );
}
