import { motion } from "framer-motion";
import { FC } from "react";
import { Styles } from "../Constants";

interface Inputs { children: React.ReactNode; onClick: () => void; }
export const BackdropComponent: FC<Inputs> = ({ children, onClick = () => {} }) =>
  <motion.div
    onClick={onClick}
    style={{ ...Styles.window, ...Styles.center, backgroundColor: "#000000CC" }}
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  >
    {children}
  </motion.div>