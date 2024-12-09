import { Constants } from "../Constants";
import { ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { GamePhase } from "../abstractions/enums";
import { GameState } from "../abstractions/states";

interface ControlZoneInputs {
  parentZone: Zone;
  gameState: GameState;
  controller: ControllerInterface;
}

export const ControlZone: React.FC<ControlZoneInputs> = ({parentZone, gameState, controller}) => {
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

  switch(gameState.phase) {
    case GamePhase.Draw:
    case GamePhase.Reserve:
      buttonText = "Bid";
      buttonAction = () => controller.onBid();
      break;
    case GamePhase.Kitty:
      buttonText = "Hide";
      buttonAction = () => controller.onHide();
      break;
    case GamePhase.Play:
      buttonText = "Play";
      buttonAction = () => controller.onPlay();
      break;
    case GamePhase.End:
      buttonText = "Next Game";
      buttonAction = () => controller.onNext();
      break;
    case GamePhase.Waiting:
      buttonText = "Waiting...";
      buttonDisabled = true;
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
            opacity: (buttonDisabled) ? "0.4" : "1.0"
          }}>
          {buttonText}
        </button>
      )}
    </div>
  );
}
