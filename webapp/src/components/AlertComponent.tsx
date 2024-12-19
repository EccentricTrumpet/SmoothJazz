import { motion } from "framer-motion";
import { BackdropComponent } from "./BackdropComponent";
import { AlertState } from "../abstractions/states";

const dropIn = {
  hidden: {
    y: "-100vh",
    opacity: 0,
  },
  visible: {
    y: "0",
    opacity: 1,
    transition: {
      duration: 0.1,
      type: "spring",
      damping: 25,
      stiffness: 500,
    }
  },
  exit: {
    y: "100vh",
    opacity: 0,
  },
}

interface AlertComponentInputs {
  alertState: AlertState;
  onClose?: () => any;
}
export const AlertComponent: React.FC<AlertComponentInputs> = ({ alertState, onClose = () => {} }) => {
  return (
    <BackdropComponent onClick={onClose}>
      <motion.div
        onClick={e => e.stopPropagation()}
        style={{
          width: "clamp(50%, 700px, 90%)",
          height: "min(50%, 300px)",
          margin: "auto",
          flexDirection: "column",
          background: "linear-gradient(10deg, var(--primary), var(--primary-hover))",
          borderRadius: "12px",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
        variants={dropIn}
        initial="hidden"
        animate="visible"
        exit="exit"
      >
        <h2>{alertState.title}</h2>
        <h4>{alertState.message}</h4>
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