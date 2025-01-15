// React tooltip require anchor tags without href
/* eslint-disable jsx-a11y/anchor-is-valid */
import { FC, ReactNode } from "react";
import { Tooltip } from "react-tooltip";
import { CardsZone } from ".";
import { ControlInterface } from "../abstractions";
import { Position, Size, Zone } from "../abstractions/bounds";
import { MatchPhase, Seat } from "../abstractions/enums";
import { BoardState, PlayerState } from "../abstractions/states";
import { Constants } from "../Constants";

const status = (status: string): ReactNode => {
  const {codepoint, description} = Constants.statusDetails[status];
  return (
    <>
      <h3  style={{ margin: "-6px 0px -6px 0px" }}>
        <a data-tooltip-id={`${status}-tooltip`} data-tooltip-content={description}>
          {String.fromCodePoint(codepoint)}
        </a>
      </h3>
      <Tooltip id={`${status}-tooltip`} />
    </>
  )
}

interface Inputs { player: PlayerState; board: BoardState; parent: Zone; control: ControlInterface; }
export const PlayerZone: FC<Inputs> = ({player, board, parent, control}) => {

  let handZone: Zone, nameZone: Zone, playingZone: Zone, trickStatusZone: Zone, playerStatusZone: Zone;
  let nameRotate: number = 0;
  const nameHeight = 3*Constants.margin;

  switch(player.seat) {
    case Seat.North:
      handZone = new Zone(
        new Position(
          parent.left() + 2*Constants.margin + Constants.cardHeight,
          parent.top() + Constants.margin
        ),
        new Size(
          parent.size.width - 2*(2*Constants.margin + Constants.cardHeight),
          Constants.cardHeight
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight/2,
          handZone.bottom() + Constants.margin,
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      trickStatusZone = new Zone(
        new Position(
          nameZone.left() - nameHeight - Constants.margin,
          nameZone.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatusZone = new Zone(
        new Position(
          nameZone.right() + Constants.margin,
          nameZone.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      playingZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight,
          nameZone.bottom() + Constants.margin
        ),
        new Size(2*Constants.cardHeight, Constants.cardHeight)
      );
      break;
    case Seat.East:
      handZone = new Zone(
        new Position(
          parent.right() - Constants.margin - Constants.cardHeight,
          parent.top() + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parent.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      trickStatusZone = new Zone(
        new Position(
          handZone.left() - nameHeight - Constants.margin,
          handZone.center().y - Constants.cardHeight/2 - nameHeight - Constants.margin/2,
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatusZone = new Zone(
        new Position(
          handZone.left() - nameHeight - Constants.margin,
          handZone.center().y + Constants.cardHeight/2 + 1.5*Constants.margin,
        ),
        new Size(nameHeight, nameHeight)
      );
      nameZone = new Zone(
        new Position(
          handZone.left() - 2.5*Constants.margin - Constants.cardHeight/2,
          handZone.center().y - Constants.margin
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      playingZone = new Zone(
        new Position(
          handZone.left() - 2*Constants.margin - nameZone.size.height - Constants.cardHeight,
          nameZone.center().y - Constants.cardHeight
        ),
        new Size(Constants.cardHeight, 2*Constants.cardHeight)
      );
      nameRotate = -90;
      break;
    case Seat.South:
      handZone = new Zone(
        new Position(
          parent.left() + 2*Constants.margin + Constants.cardHeight,
          parent.bottom() - Constants.margin - Constants.cardHeight
        ),
        new Size(
          parent.size.width - 2*(2*Constants.margin + Constants.cardHeight),
          Constants.cardHeight
        )
      );
      nameZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight/2,
          handZone.top() - 4*Constants.margin,
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      trickStatusZone = new Zone(
        new Position(
          nameZone.left() - nameHeight - Constants.margin,
          nameZone.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatusZone = new Zone(
        new Position(
          nameZone.right() + Constants.margin,
          nameZone.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      playingZone = new Zone(
        new Position(
          handZone.center().x - Constants.cardHeight,
          nameZone.top() - Constants.margin - Constants.cardHeight
        ),
        new Size(2*Constants.cardHeight, Constants.cardHeight)
      );
      break;
    case Seat.West:
      handZone = new Zone(
        new Position(
          parent.left() + Constants.margin,
          parent.top() + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parent.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      trickStatusZone = new Zone(
        new Position(
          handZone.right() + Constants.margin,
          handZone.center().y - Constants.cardHeight/2 - nameHeight - Constants.margin/2,
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatusZone = new Zone(
        new Position(
          handZone.right() + Constants.margin,
          handZone.center().y + Constants.cardHeight/2 + 1.5*Constants.margin,
        ),
        new Size(nameHeight, nameHeight)
      );
      nameZone = new Zone(
        new Position(
          handZone.right() + 2.5*Constants.margin - (Constants.cardHeight)/2,
          handZone.center().y - Constants.margin
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      playingZone = new Zone(
        new Position(
          handZone.right() + 2*Constants.margin + nameZone.size.height,
          nameZone.center().y - Constants.cardHeight
        ),
        new Size(Constants.cardHeight, 2*Constants.cardHeight)
      );
      nameRotate = 90;
      break;
  }

  return (
    <>
      <CardsZone cards={player.play} seat={player.seat} board={board} zone={playingZone} control={control} />
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
        backgroundColor: board.activePID === player.pid ?
          "rgba(0, 255, 0, 0.5)" : Constants.backgroundColor,
        borderRadius: Constants.margin
      }}>
        <h4 style={{ margin: 0 }}>{player.name}</h4>
      </div>
      <CardsZone cards={player.hand} seat={player.seat} board={board} zone={handZone} control={control} />
      <div className="container"
        style={{
          position: "fixed",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          left: trickStatusZone.left(),
          top: trickStatusZone.top(),
          width: trickStatusZone.size.width,
          height: trickStatusZone.size.height,
          backgroundColor: Constants.backgroundColor,
        }}>
          {player.pid === board.winnerPID && (status('Winner'))}
      </div>
      <div className="container" style={{
        position: "fixed",
        marginLeft: "auto",
        marginRight: "auto",
        alignItems: "center",
        display: board.matchPhase === MatchPhase.STARTED ? "flex" : "none",
        flexDirection: player.seat === Seat.North || player.seat === Seat.South ? "row" : "column",
        left: playerStatusZone.left(),
        top: playerStatusZone.top(),
        width: playerStatusZone.size.width,
        height: playerStatusZone.size.height,
        backgroundColor: Constants.backgroundColor,
      }}>
        {player.pid === board.kittyPID && (status('Kitty'))}
        {board.defenders.includes(player.pid) ? status('Defender') : status('Attacker')}
        {status(`${player.level}`)}
      </div>
    </>
  );
}
