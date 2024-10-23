import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card } from "../abstractions/Card";
import { Suit } from "../abstractions/Suit";
import CardComponent from "../components/CardComponent";
import { DisplaySettings } from "../abstractions/DisplaySettings";

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
  const displaySettings = new DisplaySettings();
  displaySettings.cardBack = "red.png"

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

  const handleDeal = () => {
    const id = cards.length;
    const index = id % 54;
    const rank = index % 13 + 1;
    let suit = Suit.Joker;
    if (index < 13) {
      suit = Suit.Spade;
    } else if (index < 26) {
      suit = Suit.Heart;
    } else if (index < 39) {
      suit = Suit.Club;
    } else if (index < 52) {
      suit = Suit.Diamond;
    }

    let newCard = new Card(id, suit, rank);
    newCard.position.x = cards.length*25;
    setCards(prevCards => [...prevCards, newCard]);
  }

  const handleFlip = () => {
    setCards(cards => cards.map((card) => new Card(
      card.id,
      card.suit,
      card.rank,
      !card.facedown,
      card.position
    )));
  }

  const cardOnClick = (card: Card) => {
    console.log(`clicked: ${card}`);
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
        <button>Add Player</button>
        <button onClick={handleDeal}>Deal</button>
        <button onClick={handleFlip}>Flip</button>
      </div>

      { cards.map((card) => {
        return <CardComponent card={card} settings={displaySettings} onClick={cardOnClick} />
      })}
    </motion.div>
  ));
}
