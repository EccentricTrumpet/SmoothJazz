import { motion } from "framer-motion";
import { CardState, OptionsState } from "../abstractions/states";
import { Constants } from "../Constants";
import { FC } from "react";

interface CardComponentInputs {
  idx: number;
  card: CardState;
  options: OptionsState;
  onClick?: () => void;
}

export const CardComponent: FC<CardComponentInputs> = ({idx, card, options, onClick = () => {}}) => {
  const altText = card.state.facedown ? "unknown" : `${card.suit} ${card.rank}`
  const imgSource = card.state.facedown ? options.cardBack : `${card.suit}${card.rank}.png`
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
        boxShadow: card.state.highlighted ? "0 0 5px 5px var(--ins-color)" : ""
      }}
      src={require(`../assets/${imgSource}`)}
      alt={altText}
      initial={
        card.prevState
          ? {
              x: card.prevState.x(),
              y: card.prevState.y(),
              rotate: card.prevState.rotate,
            }
          : {
              x: card.state.x(),
              y: card.state.y(),
              rotate: card.state.rotate,
            }
      }
      animate={{
        x: card.state.x(),
        y: card.state.y(),
        rotate: card.state.rotate,
      }}
      transition={{
        x: { type: "linear" },
        y: { type: "linear" }
      }} />
  );
}
