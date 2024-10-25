import { motion } from "framer-motion";
import { Card } from "../abstractions/Card";
import { DisplaySettings } from "../abstractions/DisplaySettings";
import { Constants } from "../Constants";
import { IController } from "../abstractions/IController";

interface CardComponentArgument {
  idx: number;
  card: Card;
  settings: DisplaySettings;
  controller: IController;
}

const CardComponent: React.FC<CardComponentArgument> = ({idx, card, settings, controller}) => {
  const altText = card.facedown ? "unknown" : `${card.suit} ${card.rank}`
  const imgSource = card.facedown ? settings.cardBack : `${card.suit}${card.rank}.png`
  return (
    <motion.img
      key={card.id}
      onClick={() => controller.onPlayCard(card)}
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        zIndex: -idx,
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
