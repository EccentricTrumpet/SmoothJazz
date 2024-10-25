import { Constants } from "../Constants";
import { Zone } from "../abstractions/Zone";
import { IController } from "../abstractions/IController";
import { Size } from "../abstractions/Size";
import { Position } from "../abstractions/Position";


interface ControlZoneArgument {
  parentZone: Zone;
  controller: IController;
}

const ControlZone: React.FC<ControlZoneArgument> = ({parentZone, controller}) => {

  const zone = new Zone(
    new Position(
      parentZone.position.x + parentZone.size.width - Constants.margin - Constants.cardHeight,
      parentZone.position.y + parentZone.size.height - Constants.margin - Constants.cardHeight,
    ),
    new Size(Constants.cardHeight, Constants.cardHeight)
  )

  const buttonCount = 3;
  const buttonHeight = (Constants.cardHeight - (buttonCount - 1)*Constants.margin)/3;

  return (
    <div className="container" style={{
      position: "fixed",
      left: zone.position.x,
      top: zone.position.y,
      width: zone.size.width,
      height: zone.size.height,
      backgroundColor: Constants.backgroundColor,
    }}>
      <button style={{
        height: buttonHeight,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        marginBottom: Constants.margin
      }}>Add Player</button>
      <button style={{
        height: buttonHeight,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        marginBottom: Constants.margin
      }}>Deal</button>
      <button style={{
        height: buttonHeight,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}>Flip</button>
    </div>
  );
}

export default ControlZone;
