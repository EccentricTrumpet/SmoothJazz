import { motion } from "framer-motion";
import { FC } from "react";
import { Size, Vector, Zone } from "../abstractions/bounds";
import { CARD_WIDTH, MARGIN, Styles } from "../Constants";

export const LogsZone: FC<{ logs: string[]; deck: Zone; }> = ({logs, deck}) => {
  const zone = deck.outSet(Vector.Down.scale(MARGIN), new Size(3*CARD_WIDTH + 2*MARGIN, 3*MARGIN));

  return (
    <motion.div whileHover={{ height: "auto" }} style={{
      ...Styles.default,
      ...zone.position(),
      backgroundColor: "var(--muted-border-color)",
      borderRadius: MARGIN,
      borderStyle: "solid",
      overflow: "hidden",
      display: "flex",
      flexDirection: "column-reverse",
    }}>
      <ul style={{ margin: "0px 0px 0px 6px" }}>
        { logs.map((log, i) => <li style={{ margin: 0 }} key={i}>{log}</li>) }
      </ul>
    </motion.div>
  )
}
