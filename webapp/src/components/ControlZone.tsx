import { FC } from "react";
import { MARGIN, Styles, CARD_WIDTH } from "../Constants";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { GamePhase, MatchPhase } from "../abstractions/enums";
import { BoardState } from "../abstractions/states";

interface Inputs { parent: Zone; board: BoardState; }
export const ControlZone: FC<Inputs> = ({parent, board}) => {
  const zone = parent.inSet(new Vector(-MARGIN, -MARGIN), Size.square(CARD_WIDTH));
  let button = { text: "", action: () => {}, disabled: false };

  switch(board.match) {
    case MatchPhase.Created:
      button = { ...button, text: "Leave", action: () => board.control?.leave() };
      break;
    case MatchPhase.Started:
      switch(board.game) {
        case GamePhase.Draw:
          button = { ...button, text: "Bid", action: () => board.control?.bid() };
          break;
        case GamePhase.Kitty:
          button = { ...button, text: "Hide", action: () => board.control?.hide() };
          break;
        case GamePhase.Play:
          button = { ...button, text: "Play", action: () => board.control?.play() };
          break;
        case GamePhase.End:
          button = { ...button, text: "Next game", action: () => board.control?.next() };
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
    <div style={{ ...Styles.defaultCenter, ...zone.position() }}>
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
