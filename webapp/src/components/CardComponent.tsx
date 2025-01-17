import { motion } from "framer-motion";
import { FC } from "react";
import { BoardState, CardState } from "../abstractions/states";
import { Styles } from "../Constants";

interface Inputs { i: number; card: CardState; board: BoardState; onClick?: () => void; }
export const CardComponent: FC<Inputs> = ({i, card, board, onClick = () => {}}) => {
  const initial = card.prev ?? card.next;
  return (
    <motion.img
      onClick={onClick}
      style={{
        ...Styles.card, position: "fixed", top: 0, left: 0, zIndex: i,
        boxShadow: card.next.highlight ? "0 0 5px 5px var(--ins-color)" : ""
      }}
      initial={{ x: initial.x(), y: initial.y(), rotate: initial.rotate }}
      animate={{ x: card.next.x(), y: card.next.y(), rotate: card.next.rotate }}
      transition={{ x: { type: "linear" }, y: { type: "linear" } }}
      src={require(`../assets/${card.next.facedown ? board.options.cardBack : card.toImg()}`)}
      alt={card.next.facedown ? "unknown" : `${card.suit} ${card.rank}`} />
  );
}
