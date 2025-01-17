import { motion } from "framer-motion";
import { FC } from "react";
import { CardState } from "../abstractions/states";
import { Styles } from "../Constants";

interface Inputs { z: number; card: CardState; onClick?: () => void; }
export const CardComponent: FC<Inputs> = ({z, card, onClick = () => {}}) => {
  const initial = card.prev ?? card.next;
  return (
    <motion.img
      onClick={onClick}
      style={{
        ...Styles.card, position: "fixed", top: 0, left: 0, zIndex: z,
        boxShadow: card.next.focus ? "0 0 5px 5px var(--ins-color)" : ""
      }}
      initial={{ ...initial.position(), rotate: `${initial.turn}turn` }}
      animate={{ ...card.next.position(), rotate: `${card.next.turn}turn` }}
      transition={{ x: { type: "linear" }, y: { type: "linear" } }}
      src={require(`../assets/${card.png()}`)}
      alt="card" />
  );
}
