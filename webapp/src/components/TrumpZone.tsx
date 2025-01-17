import { FC } from "react";
import { MARGIN, Styles, CARD_WIDTH } from "../Constants";
import { Vector, Size, Zone } from "../abstractions/bounds";
import { Suit } from "../abstractions/enums";
import { TrumpState } from "../abstractions/states";

export const TrumpZone: FC<{ parent: Zone; trump: TrumpState; }> = ({parent, trump}) => {
  const suit = trump.suit;
  const card = suit === Suit.Joker || suit === Suit.Unknown ? 'J2' : `${suit}${trump.rank}`

  return (
    <div className="container" style={{
      ...Styles.default,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      overflow: "hidden",
      ...parent.inSet(new Vector(MARGIN, -MARGIN), Size.square(CARD_WIDTH)).position(),
    }}>
      <h4 style={{ marginBottom: 5 }}>Trump:</h4>
      <img style={{ ...Styles.card }} src={require(`../assets/${card}.png`)} alt={card} />
    </div>
  );
}
