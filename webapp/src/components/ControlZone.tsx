import { Constants } from "../Constants";
import { ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { GamePhase } from "../abstractions/enums";
import { GameState } from "../abstractions/states";

interface ControlZoneInputs {
  parentZone: Zone;
  gameState: GameState;
  playerId: number;
  controller: ControllerInterface;
  debug: boolean;
}

export const ControlZone: React.FC<ControlZoneInputs> = ({parentZone, gameState, playerId, controller, debug}) => {

  const zone = new Zone(
    new Position(
      parentZone.left() + parentZone.size.width - Constants.margin - Constants.cardHeight,
      parentZone.top() + parentZone.size.height - Constants.margin - Constants.cardHeight,
    ),
    new Size(Constants.cardHeight, Constants.cardHeight)
  )

  let buttonText = "";
  let buttonAction = () => {};
  let buttonDisabled = false;

  switch(gameState.phase) {
    case GamePhase.Draw:
      buttonText = "Declare";
      buttonAction = () => {
        controller.onShow(debug ? gameState.activePlayerId : playerId)
      };
      break;
    case GamePhase.Reserve:
      buttonDisabled = true;
      break;
    case GamePhase.Kitty:
      buttonText = "Hide";
      buttonAction = () => {
        controller.onHide(debug ? gameState.activePlayerId : playerId)
      };
      break;
    case GamePhase.Play:
      buttonText = "Play";
      buttonAction = () => {
        controller.onPlay(debug ? gameState.activePlayerId : playerId)
      };
      break;
    case GamePhase.End:
      buttonText = "Next Game";
      buttonAction = () => {
        controller.onNext(debug ? gameState.activePlayerId : playerId)
      };
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
          className={buttonDisabled ? "disabled" : ""}
          onClick={buttonAction}
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}>
          {buttonText}
        </button>
      )}
    </div>
  );
}
