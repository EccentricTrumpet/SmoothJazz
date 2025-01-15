import { FC } from "react";
import { Constants } from "../Constants";
import { Position, Size, Zone } from "../abstractions/bounds";
import { Suit } from "../abstractions/enums";
import { TrumpState } from "../abstractions/states";

interface TrumpZoneInputs { parentZone: Zone; trump: TrumpState; }
export const TrumpZone: FC<TrumpZoneInputs> = ({parentZone, trump}) => {
  const zone = new Zone(
    new Position(
      parentZone.left() + Constants.margin,
      parentZone.top() + parentZone.size.height - Constants.margin - Constants.cardHeight,
    ),
    new Size(Constants.cardHeight, Constants.cardHeight)
  );
  const trumpCard = trump.suit === Suit.Joker || trump.suit === Suit.Unknown
    ? 'J2' : `${trump.suit}${trump.rank}`

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
        src={require(`../assets/${trumpCard}.png`)}
        alt={trumpCard}
      />
    </div>
  );
}
