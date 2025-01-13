import { FC } from "react";
import { Constants } from "../Constants";
import { Position, Size, Zone } from "../abstractions/bounds";
import { Suit } from "../abstractions/enums";
import { TrumpState } from "../abstractions/states";

interface TrumpZoneInputs {
  parentZone: Zone;
  trumpState: TrumpState;
}

export const TrumpZone: FC<TrumpZoneInputs> = ({parentZone, trumpState}) => {
  const zone = new Zone(
    new Position(
      parentZone.left() + Constants.margin,
      parentZone.top() + parentZone.size.height - Constants.margin - Constants.cardHeight,
    ),
    new Size(Constants.cardHeight, Constants.cardHeight)
  );
  const trump = trumpState.trumpSuit === Suit.Joker || trumpState.trumpSuit === Suit.Unknown
    ? 'J2' : `${trumpState.trumpSuit}${trumpState.trumpRank}`

  return (
    <div className="container" style={{
      position: "fixed",
      left: zone.left(),
      top: zone.top(),
      width: zone.size.width,
      height: zone.size.height,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      overflow: "hidden",
      backgroundColor: Constants.backgroundColor,
    }}>
      <h4 style={{ marginBottom: 10 }}>Trump:</h4>
      <img
        style={{
          width: Constants.cardWidth,
          height: Constants.cardHeight,
          borderRadius: Constants.cardRadius,
          borderStyle: "solid",
        }}
        src={require(`../assets/${trump}.png`)}
        alt={trump}
      />
    </div>
  );
}
