import { motion } from "framer-motion";
import { Card } from "../abstractions/Card";
import { DisplaySettings } from "../abstractions/DisplaySettings";
import { Constants } from "../Constants";

type CallbackType = (card: Card) => any;

interface CardComponentArgument {
  card: Card;
  settings: DisplaySettings;
  onClick: CallbackType;
}

const CardComponent: React.FC<CardComponentArgument> = ({card, settings, onClick}) => {
  const altText = card.facedown ? "unknown" : `${card.suit} ${card.rank}`
  const imgSource = card.facedown ? settings.cardBack : `${card.suit}${card.rank}.png`
  return (
    <motion.img
      key={card.id}
      onClick={() => onClick(card)}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: -card.position.z,
        width: Constants.cardWidth,
        height: Constants.cardHeight,
        borderRadius: Constants.cardRadius,
        borderStyle: "solid"
      }}
      src={require(`../assets/${imgSource}`)}
      alt={altText}
      initial={{ x: 0, y: 0 }}
      animate={{ x: card.position.x, y: card.position.y }}
      transition={{
        x: { type: "linear" },
        y: { type: "linear" }
      }} />
  );
}

export default CardComponent;
