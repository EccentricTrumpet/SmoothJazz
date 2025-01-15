import { motion } from "framer-motion";
import { CardState, OptionsState } from "../abstractions/states";
import { Constants } from "../Constants";
import { FC } from "react";

interface Inputs { idx: number; card: CardState; options: OptionsState; onClick?: () => void; }
export const CardComponent: FC<Inputs> = ({idx, card, options, onClick = () => {}}) => {
  const altText = card.next.facedown ? "unknown" : `${card.suit} ${card.rank}`
  const imgSource = card.next.facedown ? options.cardBack : `${card.suit}${card.rank}.png`
  const initial = card.prev ?? card.next;
  return (
    <motion.img
      onClick={onClick}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: idx,
        width: Constants.cardWidth,
        height: Constants.cardHeight,
        borderRadius: Constants.cardRadius,
        borderStyle: "solid",
        boxShadow: card.next.highlighted ? "0 0 5px 5px var(--ins-color)" : ""
      }}
      initial={{ x: initial.x(), y: initial.y(), rotate: initial.rotate }}
      animate={{ x: card.next.x(), y: card.next.y(), rotate: card.next.rotate }}
      transition={{ x: { type: "linear" }, y: { type: "linear" } }}
      src={require(`../assets/${imgSource}`)}
      alt={altText} />
  );
}
