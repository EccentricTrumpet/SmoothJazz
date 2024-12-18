import { motion } from "framer-motion";

interface BackdropComponentInputs {
  children: React.ReactNode;
  onClick?: () => any;
}
export const BackdropComponent: React.FC<BackdropComponentInputs> = ({ children, onClick = () => { } }) => {
  return (
    <motion.div
      onClick={onClick}
      style={{
        position: "absolute",
        top: "0",
        left: "0",
        height: "100%",
        width: "100%",
        backgroundColor: "#000000CC",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {children}
    </motion.div>
  )
}