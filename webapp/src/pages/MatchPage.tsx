import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card } from "../abstractions/Card";
import { Player } from "../abstractions/Player";

export default function MatchPage() {
  const [socket, setSocket] = useState<Socket>();
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });
  const { id } = useParams();
  const { state } = useLocation();
  const name = state.name;
  const [cards, setCards] = useState<Array<Card>>([]);

  // Establish window size
  useEffect(() => {
    const handleResize = debounce(() => {
      console.log(`Resizing - width: ${window.innerWidth}, height: ${window.innerHeight}`);
      setSize({ width: window.innerWidth, height: window.innerHeight });
    }, 100);
    window.addEventListener("resize", handleResize);
    return () => {
      handleResize.cancel();
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  // Establish socket connection
  useEffect(() => {
    console.log('establishing connection')

    const manager = new Manager("localhost:5001")
    const matchSocket = manager.socket("/match")

    matchSocket.on("disconnect", () => {
      console.log('socket disconnected');
    });

    matchSocket.on("connect", () => {
      setSocket(matchSocket)
      console.log('socket connected');
    });

    return () => {
      // Teardown
      matchSocket.off("connect")
      matchSocket.disconnect();
      matchSocket.off("disconnect")
    };
  }, []);

  // Configure messages
  useEffect(() => {
    if (socket) {
      // Receive messages
      socket.on("data", (data) => {
      });

      socket.on("leave", (player_name) => {
        console.log(`${player_name} has left the match`);
      });

      socket.on("join", (player_name) => {
        console.log(`${player_name} has joined the match`);
      });

      // Join match
      socket.emit("join", name, id);

      return () => {
        // Teardown
        socket.off("data");
        socket.off("join");
        socket.emit("leave", name, id);
        socket.off("leave");
      };
    }
  }, [socket, name, id]);

  const handleDealCard = () => {
    let newCard = new Card("king_of_hearts2.png", "j");
    newCard.setX(cards.length*10);
    setCards(prevCards => [...prevCards, newCard]);
  }

  return (
    !socket ? (
      <p>Loading ...</p>
    ) : (
    <motion.div style={{
      display: "grid",
      placeContent: "center",
      width: "100vw",
      height: "100vh",
    }}>
      <div className="grid" style={{
        width: "500px"
      }}>
        <button>New Player</button>
        <button onClick={handleDealCard}>Deal Card</button>
        <button>Play Card</button>
      </div>

      { cards.map((card, idx) => {
        return <motion.img
          style={{position: "fixed", top: 0, left: 0}}
          key={idx}
          src={require(`../assets/${card.suit}`)}
          alt={card.rank}
          initial={{ x: 0, y: 0 }}
          animate={{ x: card.x, y: 100 }}
          transition={{
            x: { type: "spring", stiffness: 100 }
          }} />
      })}
    </motion.div>
  ));
}
