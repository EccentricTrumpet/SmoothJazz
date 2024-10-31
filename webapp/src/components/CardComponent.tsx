import { motion } from "framer-motion";
import { Card } from "../abstractions";
import { OptionsState } from "../abstractions/states";
import { Constants } from "../Constants";

interface CardComponentInputs {
  idx: number;
  card: Card;
  options: OptionsState;
  onClick?: () => any;
  animate?: boolean;
}

export const CardComponent: React.FC<CardComponentInputs> = ({idx, card, options, onClick = () => {}}) => {
  const altText = card.state?.facedown ? "unknown" : `${card.suit} ${card.rank}`
  const imgSource = card.state?.facedown ? options.cardBack : `${card.suit}${card.rank}.png`
  return (
    <motion.img
      key={card.id}
      onClick={() => onClick()}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: idx,
        width: Constants.cardWidth,
        height: Constants.cardHeight,
        borderRadius: Constants.cardRadius,
        borderStyle: "solid",
      }}
      src={require(`../assets/${imgSource}`)}
      alt={altText}
      initial={
        card.prevState
          ? {
              x: card.prevState.position.x,
              y: card.prevState.position.y,
              rotate: card.prevState.rotate,
            }
          : {
              x: card.state?.position.x,
              y: card.state?.position.y,
              rotate: card.state?.rotate,
            }
      }
      animate={{
        x: card.state?.position.x,
        y: card.state?.position.y,
        rotate: card.state?.rotate,
      }}
      transition={{
        x: { type: "linear" },
        y: { type: "linear" }
      }} />
  );
}
