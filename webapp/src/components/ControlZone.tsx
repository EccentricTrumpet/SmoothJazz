import { FC } from "react";
import { MARGIN, Styles, CARD_WIDTH } from "../Constants";
import { IControl } from "../abstractions";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase } from "../abstractions/enums";
import { BoardState } from "../abstractions/states";

interface Inputs { parent: Zone; board: BoardState; control: IControl; }
export const ControlZone: FC<Inputs> = ({parent, board, control}) => {
  const zone = parent.inSet(new Vector(-MARGIN, -MARGIN), Size.square(CARD_WIDTH));
  let button = { text: "", action: () => {}, disabled: false };

  switch(board.matchPhase) {
    case MatchPhase.Created:
      button = { ...button, text: "Leave", action: () => control.leave() };
      break;
    case MatchPhase.Started:
      switch(board.gamePhase) {
        case GamePhase.Draw:
          button = { ...button, text: "Bid", action: () => control.bid() };
          break;
        case GamePhase.Kitty:
          button = { ...button, text: "Hide", action: () => control.hide() };
          break;
        case GamePhase.Play:
          button = { ...button, text: "Play", action: () => control.play() };
          break;
        case GamePhase.End:
          button = { ...button, text: "Next game", action: () => control.next() };
          break;
        case GamePhase.Waiting:
          button = { ...button, text: "Waiting...", disabled: true };
          break;
      }
      break;
    case MatchPhase.Paused:
      button = { ...button, text: "Match paused", disabled: true };
      break;
    case MatchPhase.Ended:
      button = { ...button, text: "Match ended", disabled: true };
      break;
  }

  return (
    <div className="container" style={{ ...Styles.defaultCenter, ...zone.position() }}>
      {button.text?.length > 0 && (
        <button
          style={{ ...Styles.center, margin: "0", opacity: button.disabled ? "0.4" : "1.0" }}
          className={(button.disabled) ? "disabled" : ""}
          onClick={button.action}
        >
          {button.text}
        </button>
      )}
    </div>
  );
}
