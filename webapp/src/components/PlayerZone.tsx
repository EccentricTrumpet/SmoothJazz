// React tooltip require anchor tags without href
/* eslint-disable jsx-a11y/anchor-is-valid */
import { motion } from "framer-motion";
import { FC } from "react";
import { Tooltip } from "react-tooltip";
import { CardsZone } from ".";
import { IControl } from "../abstractions";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { MatchPhase, Seat } from "../abstractions/enums";
import { BoardState, PlayerState } from "../abstractions/states";
import { BACKGROUND, CARD_HEIGHT, CARD_WIDTH, MARGIN, STATUS_CODES, Styles } from "../Constants";

const status = (status: string) => {
  const {codepoint, description} = STATUS_CODES[status];
  return (
    <h3 style={{ margin: "-6px 0px -6px 0px" }}>
      <a data-tooltip-id={`${status}-tooltip`} data-tooltip-content={description}>
        {String.fromCodePoint(codepoint)}
      </a>
      <Tooltip style={{ fontSize: "20px" }} id={`${status}-tooltip`} />
    </h3>
  );
}

const settings: { [id in Seat]: { turn: number, inset: Vector, side: Vector } } = {
  [Seat.East]: { turn: -0.25, inset: Vector.Left, side: Vector.Down },
  [Seat.South]: { turn: 0, inset: Vector.Up, side: Vector.Right },
  [Seat.West]: { turn: 0.25, inset: Vector.Right, side: Vector.Down },
  [Seat.North]: { turn: 0, inset: Vector.Down, side: Vector.Right },
}

interface Inputs { player: PlayerState; board: BoardState; parent: Zone; control: IControl; }
export const PlayerZone: FC<Inputs> = ({player, board, parent, control}) => {
  const { turn, inset, side } = settings[player.seat];
  const name = parent.inSet(inset.scale(2.5*MARGIN), Size.square(CARD_HEIGHT))
    .midSet(new Size(CARD_HEIGHT, 3*MARGIN).turn(turn));

  const trickStatus = name.outSet(side.scale(-MARGIN), Size.square(3*MARGIN));
  const playerStatus = name.outSet(side.scale(MARGIN), Size.square(3*MARGIN));
  const play = name.outSet(inset.scale(MARGIN), new Size(2*CARD_HEIGHT, CARD_HEIGHT).turn(turn));
  const width = (turn === 0 ? parent.size.width : parent.size.height) - 2*(2*MARGIN + CARD_WIDTH);
  const handHover = inset.scale(CARD_HEIGHT/2);
  const hand = name.outSet(inset.scale(-MARGIN), new Size(width, CARD_HEIGHT).turn(turn));

  return (
    <div>
      <CardsZone cards={player.play} seat={player.seat} board={board} zone={play} control={control} />
      <div className="container" style={{
        ...Styles.center, ...name.position(), position: "fixed", borderRadius: MARGIN,
        backgroundColor: board.activePID === player.pid ? "var(--ins-color)" : BACKGROUND
      }}>
        <h4 style={{ margin: 0, rotate: `${turn}turn` }}>{player.name}</h4>
      </div>
      <div className="container" style={{ ...Styles.defaultCenter, ...trickStatus.position() }} >
        { player.pid === board.winnerPID && status('Winner') }
      </div>
      <div className="container" style={{
        ...Styles.default, ...playerStatus.position(), alignItems: "center",
        flexDirection: turn === 0 ? "row" : "column",
        display: board.matchPhase === MatchPhase.Started ? "flex" : "none",
      }}>
        { player.pid === board.kittyPID && status('Kitty') }
        { board.defenders.includes(player.pid) ? status('Defender') : status('Attacker') }
        { status(`${player.level}`) }
      </div>
      <motion.div whileHover={handHover.position()}>
        <CardsZone cards={player.hand} seat={player.seat} board={board} zone={hand} control={control} />
      </motion.div>
    </div>
  )
}
