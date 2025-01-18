import { motion } from "framer-motion";
import { FC, useEffect } from "react";
import { ErrorState } from "../abstractions/states";
import { Styles } from "../Constants";
import { BackdropComponent } from "./BackdropComponent";

const dropIn = {
  hidden: { y: "-100vh", opacity: 0 },
  visible: { y: "0", opacity: 1, transition: { type: "spring", damping: 25, stiffness: 500 } },
  exit: { y: "100vh", opacity: 0 },
}

interface Inputs { error: ErrorState; onClose: () => void; }
export const Error: FC<Inputs> = ({ error, onClose }) => {
  // Close on space bar
  useEffect(() => {
    const esc = (e: KeyboardEvent) => e.key === 'Escape' ? onClose() : console.log();
    document.addEventListener('keydown', esc);
    return () => document.removeEventListener('keydown', esc);
  }, [onClose]);

  return (
    <BackdropComponent onClick={onClose}>
      <motion.div
        onClick={e => e.stopPropagation()}
        style={{
          ...Styles.center,
          width: "clamp(50%, 700px, 90%)",
          height: "min(50%, 300px)",
          margin: "auto",
          flexDirection: "column",
          background: "linear-gradient(10deg, var(--primary), var(--primary-hover))",
          borderRadius: "12px",
        }}
        variants={dropIn}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        <h2>{error.title}</h2>
        <h4>{error.message}</h4>
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={onClose}
          style={{ width: "fit-content" }}
        >
          Close
        </motion.button>
      </motion.div>
    </BackdropComponent>
  )
}