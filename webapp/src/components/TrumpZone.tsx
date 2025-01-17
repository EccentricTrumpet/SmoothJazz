import { FC } from "react";
import { MARGIN, Styles, CARD_WIDTH } from "../Constants";
import { Point, Size, Zone } from "../abstractions/bounds";
import { Suit } from "../abstractions/enums";
import { TrumpState } from "../abstractions/states";

export const TrumpZone: FC<{ parent: Zone; trump: TrumpState; }> = ({parent, trump}) => {
  const card = trump.suit === Suit.Joker || trump.suit === Suit.Unknown ? 'J2' : `${trump.suit}${trump.rank}`

  return (
    <div className="container" style={{
      ...Styles.default,
      ...parent.inSet(new Point(MARGIN, -MARGIN), new Size(CARD_WIDTH, CARD_WIDTH)).css(),
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      overflow: "hidden",
    }}>
      <h4 style={{ marginBottom: 5 }}>Trump:</h4>
      <img style={{ ...Styles.card }} src={require(`../assets/${card}.png`)} alt={card} />
    </div>
  );
}
