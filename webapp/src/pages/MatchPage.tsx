import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import { Manager, Socket } from "socket.io-client";
import { debounce } from "lodash";
import { Card } from "../abstractions/Card";
import { Suit } from "../abstractions/Suit";
import { DisplaySettings } from "../abstractions/DisplaySettings";
import { Constants } from "../Constants";
import { Zone } from "../abstractions/Zone";
import { Position } from "../abstractions/Position";
import { Size } from "../abstractions/Size";
import { IController } from "../abstractions/IController";
import ControlZone from "../components/ControlZone";
import PlayerZone from "../components/PlayerZone";
import { PlayerState } from "../abstractions/PlayerState";
import { SeatPosition } from "../abstractions/SeatPosition";

export default function MatchPage() {
  // React states
  const { id } = useParams();
  const { state } = useLocation();

  // API states
  const [socket, setSocket] = useState<Socket>();

  // Game states
  const name = state.name;
  const [cards, setCards] = useState<Array<Card>>([]);

  // UI states
  const [zone, setZone] = useState(new Zone(
    new Position(0, 0),
    new Size(window.innerWidth, window.innerHeight)
  ));
  const [players, setPlayers] = useState([
    new PlayerState("Alice", 0, SeatPosition.South, []),
    new PlayerState("Bob", 0, SeatPosition.East, []),
    new PlayerState("Charlie", 0, SeatPosition.North, []),
    new PlayerState("David", 0, SeatPosition.West, []),
  ])
  const displaySettings = new DisplaySettings("red.png");

  // Establish window size
  useEffect(() => {
    const handleResize = debounce(() => {
      setZone(new Zone(
        new Position(0, 0),
        new Size(window.innerWidth, window.innerHeight)
      ));
    }, 1);
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
      card.selected,
      card.position
    )));
  }

  class Controller implements IController {
    onPlayCard = (card: Card) => {
      console.log(`clicked: ${card}`);
    }
  }

  const gameController = new Controller();

  return (
    !socket ? (
      <p>Loading ...</p>
    ) : (
    <motion.div style={{
      display: "grid",
      placeContent: "center",
      width: "100vw",
      height: "100vh"
    }}>
      <ControlZone parentZone={zone} controller={gameController} />
      { players.map((player) => {
        return <PlayerZone player={player} parentZone={zone} settings={displaySettings} controller={gameController} />
      })}
    </motion.div>
  ));
}
