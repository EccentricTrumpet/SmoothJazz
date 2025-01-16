import { FC } from "react";
import { Constants, Styles } from "../Constants";
import { Point, Size, Zone } from "../abstractions/bounds";
import { Suit } from "../abstractions/enums";
import { TrumpState } from "../abstractions/states";

export const TrumpZone: FC<{ parent: Zone; trump: TrumpState; }> = ({parent, trump}) => {
  const zone = new Zone(
    new Point(
      parent.left() + Constants.margin,
      parent.top() + parent.size.height - Constants.margin - Constants.cardHeight,
    ),
    new Size(Constants.cardHeight, Constants.cardHeight)
  );
  const card = trump.suit === Suit.Joker || trump.suit === Suit.Unknown ? 'J2' : `${trump.suit}${trump.rank}`

  return (
    <div className="container" style={{
      ...Styles.default,
      ...zone.css(),
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      overflow: "hidden",
    }}>
      <h4 style={{ marginBottom: 10 }}>Trump:</h4>
      <img style={{ ...Styles.card }} src={require(`../assets/${card}.png`)} alt={card} />
    </div>
  );
}
