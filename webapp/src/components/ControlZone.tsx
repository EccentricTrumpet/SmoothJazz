import { Constants } from "../Constants";
import { ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase } from "../abstractions/enums";
import { StatusState } from "../abstractions/states";

interface ControlZoneInputs {
  parentZone: Zone;
  statusState: StatusState;
  controller: ControllerInterface;
}

export const ControlZone: React.FC<ControlZoneInputs> = ({parentZone, statusState, controller}) => {
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

  switch(statusState.matchPhase) {
    case MatchPhase.CREATED:
      buttonText = "Leave";
      buttonAction = () => controller.onLeave();
      break;
    case MatchPhase.STARTED:
      switch(statusState.gamePhase) {
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
