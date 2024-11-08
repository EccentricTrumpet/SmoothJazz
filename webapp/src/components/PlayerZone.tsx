import { ControllerInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { Seat } from "../abstractions/enums";
import { OptionsState, PlayerState, TrumpState } from "../abstractions/states";
import { Constants } from "../Constants";
import { CardsZone } from ".";

interface PlayerZoneArgument {
  player: PlayerState;
  activePlayerId: number;
  trumpState: TrumpState;
  parentZone: Zone;
  options: OptionsState;
  controller: ControllerInterface;
}

export const PlayerZone: React.FC<PlayerZoneArgument> = ({player, activePlayerId, trumpState, parentZone, options, controller}) => {

  let handZone: Zone;
  let nameZone: Zone;
  let stagingZone: Zone;
  let nameRotate: number = 0;

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
        new Size(Constants.cardHeight, 3*Constants.margin)
      );
      stagingZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight,
          nameZone.bottom() + Constants.margin
        ),
        new Size(
          2*Constants.cardHeight,
          Constants.cardHeight
        )
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
          handZone.left() - 2.5*Constants.margin - Constants.cardHeight/2,
          handZone.center().y - Constants.margin
        ),
        new Size(Constants.cardHeight, 3*Constants.margin)
      );
      stagingZone = new Zone(
        new Position(
          handZone.left() - 2*Constants.margin - nameZone.size.height - Constants.cardHeight,
          nameZone.center().y - Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          2*Constants.cardHeight,
        )
      );
      nameRotate = -90;
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
          handZone.top() - 4*Constants.margin,
        ),
        new Size(Constants.cardHeight, 3*Constants.margin)
      );
      stagingZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight,
          nameZone.top() - Constants.margin - Constants.cardHeight
        ),
        new Size(
          2*Constants.cardHeight,
          Constants.cardHeight
        )
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
          handZone.right() + 2.5*Constants.margin - (Constants.cardHeight)/2,
          handZone.center().y - Constants.margin
        ),
        new Size(Constants.cardHeight, 3*Constants.margin)
      );
      stagingZone = new Zone(
        new Position(
          handZone.right() + 2*Constants.margin + nameZone.size.height,
          nameZone.center().y - Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          2*Constants.cardHeight,
        )
      );
      nameRotate = 90;
      break;
  }

  return (
    <>
      <CardsZone cards={player.staging} seat={player.seat} trumpState={trumpState} zone={stagingZone} options={options} controller={controller} />
      <div className="container" style={{
        position: "fixed",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        left: nameZone.left(),
        top: nameZone.top(),
        width: nameZone.size.width,
        height: nameZone.size.height,
        rotate: `${nameRotate}deg`,
        backgroundColor: activePlayerId === player.id ? "rgba(0, 255, 0, 0.5)" : Constants.backgroundColor,
        borderRadius: Constants.margin
      }}>
        <h4 style={{ margin: 0 }}>{player.name}</h4>
      </div>
      <CardsZone cards={player.hand} seat={player.seat} trumpState={trumpState} zone={handZone} options={options} controller={controller} />
    </>
  );
}
