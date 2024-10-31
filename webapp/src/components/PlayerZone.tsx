import { ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { OptionsState, PlayerState } from "../abstractions/states";
import { Constants } from "../Constants";
import { HandZone } from ".";

interface PlayerZoneArgument {
  player: PlayerState;
  parentZone: Zone;
  options: OptionsState;
  controller: ControllerInterface;
}

export const PlayerZone: React.FC<PlayerZoneArgument> = ({player, parentZone, options, controller}) => {

  let handZone: Zone;
  let nameZone: Zone;

  switch(player.seat) {
    case Seat.North:
      handZone = new Zone(
        new Position(
          parentZone.left() + 2*Constants.margin + Constants.cardHeight,
          parentZone.top() + Constants.margin
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
    case Seat.East:
      handZone = new Zone(
        new Position(
          parentZone.right() - Constants.margin - Constants.cardHeight,
          parentZone.top() + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parentZone.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.left(),
          handZone.top() - 3*Constants.margin
        ),
        new Size(Constants.cardHeight, 2*Constants.margin)
      );
      break;
    case Seat.South:
      handZone = new Zone(
        new Position(
          parentZone.left() + 2*Constants.margin + Constants.cardHeight,
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
          handZone.top() - 3*Constants.margin,
        ),
        new Size(Constants.cardHeight, 2*Constants.margin)
      );
      break;
    case Seat.West:
      handZone = new Zone(
        new Position(
          parentZone.left() + Constants.margin,
          parentZone.top() + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parentZone.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.left(),
          handZone.top() - 3*Constants.margin
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
        left: nameZone.left(),
        top: nameZone.top(),
        width: nameZone.size.width,
        height: nameZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        <h4 style={{ margin: 0 }}>{player.name}</h4>
      </div>
      <HandZone player={player} zone={handZone} options={options} controller={controller} />
    </>
  );
}
