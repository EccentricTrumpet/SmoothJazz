import { Constants } from "../Constants";
import { Zone } from "../abstractions/Zone";
import { IController } from "../abstractions/IController";
import { Size } from "../abstractions/Size";
import { Position } from "../abstractions/Position";
import { PlayerState } from "../abstractions/PlayerState";
import { DisplaySettings } from "../abstractions/DisplaySettings";
import { SeatPosition } from "../abstractions/SeatPosition";
import HandZone from "./HandZone";


interface ControlZoneArgument {
  player: PlayerState;
  parentZone: Zone;
  settings: DisplaySettings;
  controller: IController;
}

const ControlZone: React.FC<ControlZoneArgument> = ({player, parentZone, settings, controller}) => {

  let handZone: Zone;
  let nameZone: Zone;

  switch(player.seatPosition) {
    case SeatPosition.North:
      handZone = new Zone(
        new Position(
          parentZone.position.x + 2*Constants.margin + Constants.cardHeight,
          parentZone.position.y + Constants.margin
        ),
        new Size(
          parentZone.size.width - 2*(2*Constants.margin + Constants.cardHeight),
          Constants.cardHeight
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight/2,
          handZone.bottom() + Constants.margin,
        ),
        new Size(Constants.cardHeight, 2*Constants.margin)
      );
      break;
    case SeatPosition.East:
      handZone = new Zone(
        new Position(
          parentZone.right() - Constants.margin - Constants.cardHeight,
          parentZone.position.y + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parentZone.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.position.x,
          handZone.position.y - 3*Constants.margin
        ),
        new Size(Constants.cardHeight, 2*Constants.margin)
      );
      break;
    case SeatPosition.South:
      handZone = new Zone(
        new Position(
          parentZone.position.x + 2*Constants.margin + Constants.cardHeight,
          parentZone.bottom() - Constants.margin - Constants.cardHeight
        ),
        new Size(
          parentZone.size.width - 2*(2*Constants.margin + Constants.cardHeight),
          Constants.cardHeight
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight/2,
          handZone.position.y - 3*Constants.margin,
        ),
        new Size(Constants.cardHeight, 2*Constants.margin)
      );
      break;
    case SeatPosition.West:
      handZone = new Zone(
        new Position(
          parentZone.position.x + Constants.margin,
          parentZone.position.y + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parentZone.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.position.x,
          handZone.position.y - 3*Constants.margin
        ),
        new Size(Constants.cardHeight, 2*Constants.margin)
      );
      break;
  }

  return (
    <>
      <div className="container" style={{
        position: "fixed",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        left: nameZone.position.x,
        top: nameZone.position.y,
        width: nameZone.size.width,
        height: nameZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        <h4 style={{ margin: 0 }}>{player.name}</h4>
      </div>
      <HandZone player={player} zone={handZone} settings={settings} controller={controller} />
    </>
  );
}

export default ControlZone;
