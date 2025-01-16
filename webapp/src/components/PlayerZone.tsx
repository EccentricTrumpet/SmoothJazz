// React tooltip require anchor tags without href
/* eslint-disable jsx-a11y/anchor-is-valid */
import { FC, ReactNode } from "react";
import { Tooltip } from "react-tooltip";
import { CardsZone } from ".";
import { IControl } from "../abstractions";
import { Point, Size, Zone } from "../abstractions/bounds";
import { MatchPhase, Seat } from "../abstractions/enums";
import { BoardState, PlayerState } from "../abstractions/states";
import { Constants, Styles } from "../Constants";

const status = (status: string): ReactNode => {
  const {codepoint, description} = Constants.statusDetails[status];
  return (
    <h3 style={{ margin: "-6px 0px -6px 0px" }}>
      <a data-tooltip-id={`${status}-tooltip`} data-tooltip-content={description}>
        {String.fromCodePoint(codepoint)}
      </a>
      <Tooltip style={{ fontSize: "20px" }} id={`${status}-tooltip`} />
    </h3>
  );
}

interface Inputs { player: PlayerState; board: BoardState; parent: Zone; control: IControl; }
export const PlayerZone: FC<Inputs> = ({player, board, parent, control}) => {
  let hand: Zone, name: Zone, play: Zone, trickStatus: Zone, playerStatus: Zone;
  let nameRotate: number = 0;
  const nameHeight = 3*Constants.margin;

  switch(player.seat) {
    case Seat.North:
      hand = new Zone(
        new Point(
          parent.left() + 2*Constants.margin + Constants.cardHeight,
          parent.top() + Constants.margin
        ),
        new Size(
          parent.size.width - 2*(2*Constants.margin + Constants.cardHeight),
          Constants.cardHeight
        )
      );
      name = new Zone(
        new Point(
          hand.center().x - Constants.cardHeight/2,
          hand.bottom() + Constants.margin,
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      trickStatus = new Zone(
        new Point(
          name.left() - nameHeight - Constants.margin,
          name.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatus = new Zone(
        new Point(
          name.right() + Constants.margin,
          name.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      play = new Zone(
        new Point(
          hand.center().x - Constants.cardHeight,
          name.bottom() + Constants.margin
        ),
        new Size(2*Constants.cardHeight, Constants.cardHeight)
      );
      break;
    case Seat.East:
      hand = new Zone(
        new Point(
          parent.right() - Constants.margin - Constants.cardHeight,
          parent.top() + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parent.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      trickStatus = new Zone(
        new Point(
          hand.left() - nameHeight - Constants.margin,
          hand.center().y - Constants.cardHeight/2 - nameHeight - Constants.margin/2,
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatus = new Zone(
        new Point(
          hand.left() - nameHeight - Constants.margin,
          hand.center().y + Constants.cardHeight/2 + 1.5*Constants.margin,
        ),
        new Size(nameHeight, nameHeight)
      );
      name = new Zone(
        new Point(
          hand.left() - 2.5*Constants.margin - Constants.cardHeight/2,
          hand.center().y - Constants.margin
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      play = new Zone(
        new Point(
          hand.left() - 2*Constants.margin - name.size.height - Constants.cardHeight,
          name.center().y - Constants.cardHeight
        ),
        new Size(Constants.cardHeight, 2*Constants.cardHeight)
      );
      nameRotate = -90;
      break;
    case Seat.South:
      hand = new Zone(
        new Point(
          parent.left() + 2*Constants.margin + Constants.cardHeight,
          parent.bottom() - Constants.margin - Constants.cardHeight
        ),
        new Size(
          parent.size.width - 2*(2*Constants.margin + Constants.cardHeight),
          Constants.cardHeight
        )
      );
      name = new Zone(
        new Point(
          hand.center().x - Constants.cardHeight/2,
          hand.top() - 4*Constants.margin,
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      trickStatus = new Zone(
        new Point(
          name.left() - nameHeight - Constants.margin,
          name.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatus = new Zone(
        new Point(
          name.right() + Constants.margin,
          name.top(),
        ),
        new Size(nameHeight, nameHeight)
      );
      play = new Zone(
        new Point(
          hand.center().x - Constants.cardHeight,
          name.top() - Constants.margin - Constants.cardHeight
        ),
        new Size(2*Constants.cardHeight, Constants.cardHeight)
      );
      break;
    case Seat.West:
      hand = new Zone(
        new Point(
          parent.left() + Constants.margin,
          parent.top() + 2*Constants.margin + Constants.cardHeight
        ),
        new Size(
          Constants.cardHeight,
          parent.size.height - 2*(2*Constants.margin + Constants.cardHeight)
        )
      );
      trickStatus = new Zone(
        new Point(
          hand.right() + Constants.margin,
          hand.center().y - Constants.cardHeight/2 - nameHeight - Constants.margin/2,
        ),
        new Size(nameHeight, nameHeight)
      );
      playerStatus = new Zone(
        new Point(
          hand.right() + Constants.margin,
          hand.center().y + Constants.cardHeight/2 + 1.5*Constants.margin,
        ),
        new Size(nameHeight, nameHeight)
      );
      name = new Zone(
        new Point(
          hand.right() + 2.5*Constants.margin - (Constants.cardHeight)/2,
          hand.center().y - Constants.margin
        ),
        new Size(Constants.cardHeight, nameHeight)
      );
      play = new Zone(
        new Point(
          hand.right() + 2*Constants.margin + name.size.height,
          name.center().y - Constants.cardHeight
        ),
        new Size(Constants.cardHeight, 2*Constants.cardHeight)
      );
      nameRotate = 90;
      break;
  }

  return <>
    <CardsZone cards={player.play} seat={player.seat} board={board} zone={play} control={control} />
    <div className="container" style={{
      ...Styles.center,
      ...name.css(),
      rotate: `${nameRotate}deg`,
      position: "fixed",
      borderRadius: Constants.margin,
      backgroundColor: board.activePID === player.pid ? "var(--ins-color)" : Constants.backgroundColor
    }}>
      <h4 style={{ margin: 0 }}>{player.name}</h4>
    </div>
    <CardsZone cards={player.hand} seat={player.seat} board={board} zone={hand} control={control} />
    <div className="container"
      style={{ ...Styles.default, ...Styles.center, ...trickStatus.css() }}>
        {player.pid === board.winnerPID && (status('Winner'))}
    </div>
    <div className="container" style={{
      ...Styles.default,
      ...playerStatus.css(),
      alignItems: "center",
      display: board.matchPhase === MatchPhase.Started ? "flex" : "none",
      flexDirection: player.seat === Seat.North || player.seat === Seat.South ? "row" : "column",
    }}>
      {player.pid === board.kittyPID && (status('Kitty'))}
      {board.defenders.includes(player.pid) ? status('Defender') : status('Attacker')}
      {status(`${player.level}`)}
    </div>
  </>
}
