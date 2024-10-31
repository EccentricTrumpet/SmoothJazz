import { Constants } from "../Constants";
import { Position, Size, Zone } from "../abstractions/bounds";

interface ControlZoneInputs {
  parentZone: Zone;
}

export const ControlZone: React.FC<ControlZoneInputs> = ({parentZone}) => {

  const zone = new Zone(
    new Position(
      parentZone.left() + parentZone.size.width - Constants.margin - Constants.cardHeight,
      parentZone.top() + parentZone.size.height - Constants.margin - Constants.cardHeight,
    ),
    new Size(Constants.cardHeight, Constants.cardHeight)
  )

  const buttonCount = 3;
  const buttonHeight = (Constants.cardHeight - (buttonCount - 1)*Constants.margin)/3;

  return (
    <div className="container" style={{
      position: "fixed",
      left: zone.left(),
      top: zone.top(),
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
      }}>Test A</button>
      <button style={{
        height: buttonHeight,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        marginBottom: Constants.margin
      }}>Test B</button>
      <button style={{
        height: buttonHeight,
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}>Play</button>
    </div>
  );
}
